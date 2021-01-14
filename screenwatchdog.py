import pyscreenshot as ImageGrab
from threading import Thread
from time import sleep
from time import time as ticks
import numpy as np

class ScreenAreaWatchdogListener:
    def on_area_changed(self, identifier: int):
        pass

    def on_area_set(self, identifier: int, area: tuple):
        pass

    def on_area_reset(self, identifier: int):
        pass

    def on_screenshot(self, identifier: int):
        pass
        
    def on_exit(self, identifier: int):
        pass

class ScreenAreaWatchdog(Thread):
    def __init__(self, listener: ScreenAreaWatchdogListener = None, identifier: int = 1):
        Thread.__init__(self)
        self.oldArea: Image = None
        self.newArea: Image = None
        self.bbox: tuple = None
        self.listener: ScreenAreaWatchdogListener = listener
        self.identifier = identifier
        self.stop = False
        self.rate: float = 10.0 #check every ten seconds
        self.changed = False

    def set_bbox(self, area: tuple):
        self.bbox = area
        if self.listener is not None:
            self.listener.on_area_set(area, self.identifier)

    def log(self, logstr: str):
        print(f"{ticks():05.1f} - {logstr}")

    def reset_area(self):
        self.newArea = None
        self.changed = False
        if self.listener is not None:
            self.listener.on_area_reset(self.identifier)
        else:
            self.log("Reset area")

    def take_screenshot(self):
        if self.bbox is None or self.newArea is not None:
            return
        self.newArea = ImageGrab.grab(bbox=self.bbox)
        if self.listener is not None:
            self.listener.on_screenshot(self.identifier)
        else:
            self.log("take screenshot")

    def area_changed(self):
        # after first screenshot
        if self.oldArea is None and self.newArea is not None:
            self.oldArea = self.newArea
            self.newArea = None
            if self.listener is None:
                self.log("first screenshot")

        # we need first to screenshots to compare changes
        if self.oldArea is None or self.newArea is None:
            return False

        if self.listener is None:
            self.log("compare")
        old = np.array(self.oldArea)
        new = np.array(self.newArea)
        if old.shape != new.shape:
            return True
        return np.max(np.abs(new - old)) != 0

    def check(self):
        self.newArea = None
        self.take_screenshot()
        if self.area_changed():
            self.oldArea = self.newArea
            if self.listener is not None:
                self.changed = True
                self.listener.on_area_changed(self.identifier)
            else:
                self.log("Area changed!")

    def exit(self):
        self.stop = True

    def run(self):
        while not self.stop:
            self.check()
            sleep(self.rate)
        if self.listener:
            self.listener.on_exit(self.identifier)
