from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel,
                            QGridLayout, QFileDialog, QDesktopWidget)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtCore import pyqtSignal
import sys
from time import sleep
import yaml

class ChooseArea(QWidget):

    def __init__(self):
        super().__init__()
        self.setObjectName("ChooseArea")
        self.settings()
        self.create_widgets()
        self.set_layout()

    def closeEvent(self, event):
        self.choose()
        event.accept()

    def choose(self):
        with open('area.yml', 'w') as f:
            data = { 'x': self.x(), 'y': self.y(), 'width': self.width(), 'height': self.height() }
            yaml.dump( data, f)
            f.close()

    def set_layout(self):
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.btn_choose_area, 0,0, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def create_widgets(self):
        self.btn_choose_area = QPushButton("Choose Area")
        self.btn_choose_area.clicked.connect(self.close)

    def settings(self):
        self.resize(370, 270)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setWindowTitle("Choose Area")
        self.setWindowOpacity(0.5)

root = QApplication(sys.argv)
app = ChooseArea()
app.show()
sys.exit(root.exec_())
