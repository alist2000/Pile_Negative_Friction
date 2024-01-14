from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QLabel, QPushButton, \
    QTextEdit, QAbstractItemView, QTableWidget, \
    QRadioButton, QSpacerItem, QGraphicsView, QGraphicsScene
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QApplication, QComboBox, QTextBrowser
from PySide6.QtGui import QPixmap

import copy

from mainCalc import MainCalc
from plot import Plot
from image import ImageWindow
from Unit import Unit


class tabWidget(QWidget, Unit):
    def __init__(self):
        super().__init__()
        # Set the main window size
        self.setGeometryToCenter(930, 600)
        self.setWindowTitle("Negative Skin Friction")

        hLayout1 = QHBoxLayout()
        self.yesNoLayout = QHBoxLayout()
        hLayout2 = QHBoxLayout()

        QeLabel = QLabel("Do you want to consider the 'End Bearing Capacity' in the calculations?")
        self.yes_qe = QRadioButton("Yes")
        self.no_qe = QRadioButton("No")
        self.no_qe.setChecked(True)
        Qe = QLabel(f"Qe ({self.forceUnit}): ")
        self.QeNum = QDoubleSpinBox()
        self.QeNum.setRange(0, 10000)
        if self.no_qe.isChecked():
            self.QeNum.setEnabled(False)

        hLayout1.addWidget(QeLabel)
        self.yesNoLayout.addWidget(self.yes_qe)
        self.yesNoLayout.addWidget(self.no_qe)
        hLayout1.addLayout(self.yesNoLayout)
        hLayout1.addWidget(Qe)
        hLayout1.addWidget(self.QeNum)
        self.yes_qe.toggled.connect(self.on_button_toggled)
        self.no_qe.toggled.connect(self.on_button_toggled)
        diameter = QLabel(f"Pile Diameter ({self.lengthUnit}): ")
        diameterNum = QDoubleSpinBox()
        diameterNum.setRange(0.1, 10000)
        diameterNum.setValue(1)

        hLayout2.addWidget(diameter)
        hLayout2.addWidget(diameterNum)
        Qd = QLabel(f"Permanent load (Qd) ({self.forceUnit}): ")
        QdNum = QDoubleSpinBox()
        QdNum.setRange(0.1, 10000)
        QdNum.setValue(700)
        hLayout2.addWidget(Qd)
        hLayout2.addWidget(QdNum)

        deltaH = QLabel("\u0394H: ")
        deltaHNum = QDoubleSpinBox()
        deltaHNum.setDecimals(4)
        deltaHNum.setValue(0.1)
        deltaHNum.setRange(0.1, 1)

        hLayout2.addWidget(deltaH)
        hLayout2.addWidget(deltaHNum)

        # Add tabs to widget
        mainLayout = QHBoxLayout()
        layout = QVBoxLayout()
        soilProp = SoilProperties(self.QeNum, diameterNum, QdNum, deltaHNum, mainLayout)
        layout.addWidget(soilProp)
        runButton = QPushButton("Run")
        runButton.clicked.connect(soilProp.output)

        layout.addLayout(hLayout1)
        layout.addLayout(hLayout2)

        layout.addWidget(runButton)

        sign = QLabel("Made by: Ali Safari                     contact: ali.s.tag2000@gmail.com")
        sign.setStyleSheet("QLabel { color: rgba(0, 0, 0, 100); }")

        layout.addWidget(sign)
        mainLayout.addLayout(layout)

        self.setLayout(mainLayout)

    def on_button_toggled(self, checked):
        if "Yes" in self.sender().text() and checked:
            self.QeNum.setEnabled(True)
            self.no_qe.setChecked(False)
        elif "No" in self.sender().text() and checked:
            self.QeNum.setEnabled(False)
            self.yes_qe.setChecked(False)
            self.QeNum.setValue(0)

    def setGeometryToCenter(self, width, height):
        # Get the available screen geometry
        screen_geometry = QApplication.primaryScreen().availableGeometry()

        # Calculate the position to center the window
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2

        # Set the main window geometry
        self.setGeometry(x, y, width, height)


class SoilProperties(QWidget, Unit):
    def __init__(self, Qe, diameterNum, QdNum, deltaHNum, mainLayout, gridBase="spacing"):
        super(SoilProperties, self).__init__()
        self.Qe = Qe
        self.gridBase = gridBase
        self.diameterNum = diameterNum
        self.QdNum = QdNum
        self.deltaHNum = deltaHNum
        self.mainLayout = mainLayout
        self.Image = None
        self.layout = QVBoxLayout(self)
        self.coordinateButton = QRadioButton("Display Soil Layer as Coordinate")
        self.spacingButton = QRadioButton("Display Soil Layer as Spacing")
        self.spacingButton.setChecked(True)
        self.layoutBase = QHBoxLayout()
        self.layoutBase.addWidget(self.coordinateButton)
        self.layoutBase.addWidget(self.spacingButton)
        soilPropLabel = QLabel("Soil Properties")
        soilPropLayout = QVBoxLayout()
        soilPropLayout.addWidget(soilPropLabel)
        self.soilLayer = SoilPropDefine(self.coordinateButton, self.spacingButton)
        self.layout.addLayout(soilPropLayout)
        self.layout.addWidget(self.soilLayer)

    def output(self):
        if self.coordinateButton.isChecked():
            self.gridBase = "coordinate"
            firstCoord = 0

            # convert to spacing based.
            for i in range(1, self.soilLayer.tableWidgetXGrid.rowCount()):
                old_value = self.soilLayer.tableWidgetXGrid.cellWidget(i, 1).value()
                new_value = old_value - firstCoord
                firstCoord = copy.deepcopy(old_value)
                item = QDoubleSpinBox()
                item.setAlignment(Qt.AlignCenter)
                item.setValue(new_value)
                self.soilLayer.tableWidgetXGrid.setCellWidget(i, 1, item)
        else:
            self.gridBase = "spacing"

        gama = []
        h = []
        beta_cu = []
        beta_cu_value = []
        qf_max = []
        if self.soilLayer.tableWidgetXGrid.rowCount() < 2:  # make default soil
            gama.append(10)
            h.append(10)
            beta_cu.append("cu")
            beta_cu_value.append(70)
            qf_max.append(0)
        else:
            for i in range(1, self.soilLayer.tableWidgetXGrid.rowCount()):
                betaOrCu = self.soilLayer.tableWidgetXGrid.cellWidget(i, 2).currentText()
                if betaOrCu == "Cu":
                    betaOrCu = betaOrCu.lower()
                else:
                    betaOrCu = "beta"
                gama.append(self.soilLayer.tableWidgetXGrid.cellWidget(i, 0).value())
                h.append(self.soilLayer.tableWidgetXGrid.cellWidget(i, 1).value())
                beta_cu.append(betaOrCu)
                beta_cu_value.append(self.soilLayer.tableWidgetXGrid.cellWidget(i, 3).value())
                qf_max.append(self.soilLayer.tableWidgetXGrid.cellWidget(i, 4).value())
        Qd = self.QdNum.value()
        d_pile = self.diameterNum.value()
        delta = self.deltaHNum.value()
        Qe = self.Qe.value()
        main = MainCalc(gama, h, qf_max, beta_cu, beta_cu_value, d_pile, Qd, Qe, delta)
        plot = Plot(main.h_list, main.rn_qs, main.qs_qd)
        label = QLabel()
        pixmap = QPixmap("plot.png")
        label.setPixmap(pixmap)
        self.Image = ImageWindow()
        # self.mainLayout.addWidget(label)

    @staticmethod
    def sortCoordinate(grid):
        sortedGrid = []
        baseNumber = -float("inf")
        for data in grid:
            if data["position"] >= baseNumber:
                baseNumber = data["position"]
                sortedGrid.append(data)
            else:
                for i in range(len(sortedGrid)):
                    if data["position"] < sortedGrid[i]["position"]:
                        sortedGrid.insert(i, data)
                        break

        return sortedGrid


class SoilPropDefine(QWidget, Unit):
    def __init__(self, coordinateButton, spacingButton):
        super(SoilPropDefine, self).__init__()
        self.coordinateButton = coordinateButton
        self.spacingButton = spacingButton
        self.grid_base = None
        self.gridBase()
        if not self.grid_base:
            self.grid_base = "spacing"
        self.layout = QVBoxLayout(self)
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.coordinateButton)
        hLayout.addWidget(self.spacingButton)

        # Connect signals
        self.coordinateButton.toggled.connect(self.on_button_toggled)
        self.spacingButton.toggled.connect(self.on_button_toggled)
        self.buttonAdd = QPushButton("Add")
        self.buttonDelete = QPushButton("Delete")
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.buttonAdd)
        self.buttons_layout.addWidget(self.buttonDelete)
        self.tableWidgetXGrid = QTableWidget(0, 5)
        self.tableWidgetXGrid.insertRow(0)
        nameLabel = QLabel(f"\u03B3 ({self.densityUnit})")
        coordLabel = QLabel(f"H ({self.grid_base.capitalize()}) ({self.lengthUnit})")
        beta_or_cu = QLabel("\u03B2 or Cu")
        beta_or_cu_num = QLabel(f"\u03B2 or Cu value (None or {self.pressureUnit})")
        qf_max = QLabel(f"Qf max ({self.pressureUnit})")
        nameLabel.setAlignment(Qt.AlignCenter)
        coordLabel.setAlignment(Qt.AlignCenter)
        beta_or_cu.setAlignment(Qt.AlignCenter)
        beta_or_cu_num.setAlignment(Qt.AlignCenter)
        qf_max.setAlignment(Qt.AlignCenter)
        self.tableWidgetXGrid.setCellWidget(0, 0, nameLabel)
        self.tableWidgetXGrid.setCellWidget(0, 1, coordLabel)
        self.tableWidgetXGrid.setCellWidget(0, 2, beta_or_cu)
        self.tableWidgetXGrid.setCellWidget(0, 3, beta_or_cu_num)
        self.tableWidgetXGrid.setCellWidget(0, 4, qf_max)
        # Set cell size
        for row in range(1):
            self.tableWidgetXGrid.setRowHeight(row, 50)  # Set row height
            for col in range(5):
                self.tableWidgetXGrid.setColumnWidth(col, 155)  # Set column width
        self.layoutTable = QHBoxLayout()
        self.layoutTable.addWidget(self.tableWidgetXGrid)
        self.layoutTable.addLayout(self.buttons_layout)

        self.tableWidgetXGrid.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetXGrid.horizontalHeader().setVisible(False)  # hide column headers
        self.layout.addLayout(hLayout)
        self.layout.addLayout(self.layoutTable)

        self.setLayout(self.layout)

        self.buttonAdd.clicked.connect(self.add_item)
        self.buttonDelete.clicked.connect(self.delete_item)

    def on_button_toggled(self, checked):
        if "Coordinate" in self.sender().text() and checked:
            item = QLabel(f"H (Coordinate) {self.lengthUnit}")
            item.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(0, 1, item)
            self.grid_base = "coordinate"
            firstCoord = 0
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                old_value = self.tableWidgetXGrid.cellWidget(i, 1).value()
                new_value = firstCoord + old_value
                firstCoord = copy.deepcopy(new_value)
                item = QDoubleSpinBox()
                item.setAlignment(Qt.AlignCenter)
                if i == 1:
                    item.setRange(0, 10000)
                else:
                    item.setRange(1, 10000)
                item.setDecimals(4)
                item.setValue(new_value)
                self.tableWidgetXGrid.setCellWidget(i, 1, item)

        elif "Spacing" in self.sender().text() and checked:
            self.grid_base = "spacing"
            item = QLabel(f"H (Spacing) {self.lengthUnit}")
            item.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(0, 1, item)
            firstCoord = 0
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                old_value = self.tableWidgetXGrid.cellWidget(i, 1).value()
                new_value = old_value - firstCoord
                firstCoord = copy.deepcopy(old_value)
                item = QDoubleSpinBox()
                item.setAlignment(Qt.AlignCenter)
                item.setValue(new_value)
                self.tableWidgetXGrid.setCellWidget(i, 1, item)

    def add_item(self):
        row = self.tableWidgetXGrid.rowCount()
        self.tableWidgetXGrid.insertRow(row)
        spinBoxGamma = QDoubleSpinBox()
        spinBoxGamma.setDecimals(4)
        spinBoxGamma.setRange(0, 1000000)
        spinBoxH = QDoubleSpinBox()
        spinBoxH.setDecimals(4)
        spinBoxH.setRange(0, 1000000)
        betaCu = QComboBox()
        betaCu.addItems(["\u03B2", "Cu"])
        spinBoxBetaCu = QDoubleSpinBox()
        spinBoxBetaCu.setDecimals(4)
        spinBoxBetaCu.setRange(0, 1000000)
        spinBoxBetaQfMax = QDoubleSpinBox()
        spinBoxBetaQfMax.setDecimals(4)
        spinBoxBetaQfMax.setRange(0, 1000000)
        spinBoxGamma.setAlignment(Qt.AlignCenter)
        spinBoxH.setAlignment(Qt.AlignCenter)
        spinBoxBetaCu.setAlignment(Qt.AlignCenter)
        spinBoxBetaQfMax.setAlignment(Qt.AlignCenter)

        spinBoxGamma.setValue(20)

        spinBoxH.setValue(10)

        spinBoxBetaCu.setValue(0.5)

        spinBoxBetaQfMax.setValue(81)

        self.tableWidgetXGrid.setCellWidget(row, 0, spinBoxGamma)
        self.tableWidgetXGrid.setCellWidget(row, 1, spinBoxH)
        self.tableWidgetXGrid.setCellWidget(row, 2, betaCu)
        self.tableWidgetXGrid.setCellWidget(row, 3, spinBoxBetaCu)
        self.tableWidgetXGrid.setCellWidget(row, 4, spinBoxBetaQfMax)

    def delete_item(self):
        currentRow = self.tableWidgetXGrid.currentRow()
        if currentRow != 0:
            self.tableWidgetXGrid.removeRow(currentRow)

    def gridBase(self):
        if self.spacingButton.isChecked():
            self.grid_base = "spacing"
        else:
            self.grid_base = "coordinate"
