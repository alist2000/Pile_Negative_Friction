from PySide6.QtWidgets import QApplication, QPushButton, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap
import sys


class ImageWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Output')
        self.label = QLabel()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        pixmap = QPixmap("plot.png")
        self.label.setPixmap(pixmap)
        self.show()



class MainWindowImage(QWidget):
    def __init__(self):
        super().__init__()
        self.open_image_window()

    def open_image_window(self):
        self.image_window = ImageWindow()
        pixmap = QPixmap("plot.png")
        self.image_window.label.setPixmap(pixmap)
        self.image_window.show()


# app = QApplication(sys.argv)
# main_window = MainWindow()
# main_window.show()
# sys.exit(app.exec())
