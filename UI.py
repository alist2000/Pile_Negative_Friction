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


class tabWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pile Negative Friction")

        hLayout2 = QHBoxLayout()

        diameter = QLabel("Pile Diameter: ")
        diameterNum = QDoubleSpinBox()
        hLayout2.addWidget(diameter)
        hLayout2.addWidget(diameterNum)
        Qd = QLabel("Permanent load (Qd): ")
        QdNum = QDoubleSpinBox()
        QdNum.setRange(0, 10000)
        QdNum.setValue(100)
        hLayout2.addWidget(Qd)
        hLayout2.addWidget(QdNum)

        deltaH = QLabel("\u0394H: ")
        deltaHNum = QDoubleSpinBox()
        deltaHNum.setDecimals(4)
        deltaHNum.setValue(0.1)
        hLayout2.addWidget(deltaH)
        hLayout2.addWidget(deltaHNum)

        # Add tabs to widget
        mainLayout = QHBoxLayout()
        layout = QVBoxLayout()
        soilProp = SoilProperties(diameterNum, QdNum, deltaHNum, mainLayout)
        layout.addWidget(soilProp)
        runButton = QPushButton("Run")
        runButton.clicked.connect(soilProp.output)

        layout.addLayout(hLayout2)

        layout.addWidget(runButton)

        sign = QLabel("Made by: Ali Safari")
        layout.addWidget(sign)
        mainLayout.addLayout(layout)

        self.setLayout(mainLayout)


class SoilProperties(QWidget):
    def __init__(self, diameterNum, QdNum, deltaHNum, mainLayout, gridBase="spacing"):
        super(SoilProperties, self).__init__()
        self.gridBase = gridBase
        self.diameterNum = diameterNum
        self.QdNum = QdNum
        self.deltaHNum = deltaHNum
        self.mainLayout = mainLayout
        self.Image = None
        self.layout = QVBoxLayout(self)
        self.coordinateButton = QRadioButton("Display Soil Layer as Coordinate")
        self.spacingButton = QRadioButton("Display Soil Layer as Spacing")
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
                print(old_value)
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
        print(gama, h, beta_cu, beta_cu_value, qf_max)
        Qd = self.QdNum.value()
        d_pile = self.diameterNum.value()
        delta = self.deltaHNum.value()
        main = MainCalc(gama, h, qf_max, beta_cu, beta_cu_value, d_pile, Qd, delta)
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


class SoilPropDefine(QWidget):
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
        nameLabel = QLabel("\u03B3")
        coordLabel = QLabel(f"H ({self.grid_base.capitalize()})")
        beta_or_cu = QLabel("\u03B2 or Cu")
        beta_or_cu_num = QLabel("\u03B2 or Cu value")
        qf_max = QLabel("Qf max")
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
            item = QLabel("H (Coordinate")
            item.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(0, 1, item)
            self.grid_base = "coordinate"
            firstCoord = 0
            print("self.tableWidgetXGrid.rowCount()", self.tableWidgetXGrid.rowCount())
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
            item = QLabel("H (Spacing)")
            item.setAlignment(Qt.AlignCenter)
            self.tableWidgetXGrid.setCellWidget(0, 1, item)
            firstCoord = 0
            for i in range(1, self.tableWidgetXGrid.rowCount()):
                old_value = self.tableWidgetXGrid.cellWidget(i, 1).value()
                print(old_value)
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
