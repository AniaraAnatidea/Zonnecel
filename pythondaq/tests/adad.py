
from PySide6 import QtGui
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel
import sys
from PySide6.QtGui import QPixmap
class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.title = "PyQt5 Adding Image To Label"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300
        self.InitWindow()
 
    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon("Logo.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        vbox = QVBoxLayout()
        labelImage = QLabel(self)
        pixmap = QPixmap("Logo.png")
        labelImage.setPixmap(pixmap)
        vbox.addWidget(labelImage)
        self.setLayout(vbox)
        self.show()
 
 
 
App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())