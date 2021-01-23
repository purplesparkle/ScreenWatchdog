from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel,
                            QGridLayout, QFileDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtCore import pyqtSignal
import sys
from time import sleep


class ScreenWatcher(QThread):
    changed_signal = pyqtSignal()
    screenshot_signal = pyqtSignal()

    def __init__(self, x, y, width, height):
        QThread.__init__(self)
        self.area = None
        self.rate = 1.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.stop = False

    def on_reset(self):
        self.old = None

    def changed(self):
        if self.old is None:
            return False
        oldImg = self.old.toImage()
        newImg = self.area.toImage()
        return oldImg != newImg
        

    def run(self):
        while not self.stop:
            self.old = self.area
            self.area = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId(), self.x, self.y, self.width, self.height)
            self.screenshot_signal.emit()
            if self.changed():
                self.changed_signal.emit()
            sleep(self.rate)

class MainWindow(QWidget):
    reset_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        #print(QApplication.screens())
        self.preview_screen = None
        self.settings()
        self.create_widgets()
        self.btn_reset.hide()
        self.set_layout()
        self.setObjectName("MainWindow")
        self.changed = False
        self.screenWatcher: ScreenWatcher = None
        self.is_red = False

    def settings(self):
        self.resize(370, 270)
        self.setWindowTitle("QScreenWatchdog")
        
    def create_widgets(self):
        self.img_preview = QLabel()
        #self.img_preview.setPixmap(self.preview_screen.scaled(350,350,
        #                            Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.img_preview.hide()
        self.btn_choose_area = QPushButton("Choose Area")
        self.btn_reset = QPushButton("Reset")

        # signals connections
        self.btn_choose_area.clicked.connect(self.choose_area)
        self.btn_reset.clicked.connect(self.reset)

    def set_layout(self):
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.img_preview, 0, 0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.btn_choose_area, 2,0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.btn_reset, 2, 0, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def choose_area(self):
        self.set_screenwatcher((0,0,500,200))
        self.screenWatcher.screenshot_signal.connect(self.on_screenshot)
        self.screenWatcher.changed_signal.connect(self.on_changed)
        self.start_screenwatcher()
        self.btn_choose_area.hide()
        self.btn_reset.show()

    def take_screenshot(self):
        #self.preview_screen = QApplication.primaryScreen().grabWindow(0)
        self.preview_screen = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId(), 0, 0, 500, 500)
        self.img_preview.setPixmap(self.preview_screen.scaled(350,350,
                                    Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.show()

    def reset(self):
        self.changed = False
        self.green()

    def on_changed(self):
        self.changed = True
        self.is_red = False
        self.green()

    def on_screenshot(self):
        if self.changed and not self.is_red:
            self.red()
            self.is_red = True
        else:
            self.green()
            self.is_red = False

    def set_screenwatcher(self, dim: tuple):
        self.screenWatcher = ScreenWatcher(*dim)
        self.reset_signal.connect(self.screenWatcher.on_reset)

    def start_screenwatcher(self):
        self.screenWatcher.start()

    def red(self):
        self.setStyleSheet("#MainWindow { background-color: red; }")

    def green(self):
        self.setStyleSheet("#MainWindow { background-color: green; }")


root = QApplication(sys.argv)
app = MainWindow()
app.show()
sys.exit(root.exec_())
