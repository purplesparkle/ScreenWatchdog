import wx
from screenwatchdog import ScreenAreaWatchdogListener
from screenwatchdog import ScreenAreaWatchdog
from time import sleep

EVT_AREA_CHANGED_ID = wx.NewIdRef()
EVT_AREA_SET_ID = wx.NewIdRef()
EVT_AREA_RESET_ID = wx.NewIdRef()
EVT_SCREENSHOT_ID = wx.NewIdRef()
EVT_EXIT_ID = wx.NewIdRef()

def EVT_AREA_CHANGED(win, func):
    win.Connect(-1, -1, EVT_AREA_CHANGED_ID, func)

def EVT_AREA_SET(win, func):
    win.Connect(-1, -1, EVT_AREA_SET_ID, func)

def EVT_AREA_RESET(win, func):
    win.Connect(-1, -1, EVT_AREA_RESET_ID, func)

def EVT_SCREENSHOT(win, func):
    win.Connect(-1, -1, EVT_SCREENSHOT_ID, func)

def EVT_EXIT(win, func):
    win.Connect(-1, -1, EVT_EXIT_ID, func)

class AreaChangedEvent(wx.PyEvent):
    def __init__(self, identifier):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_AREA_CHANGED_ID)
        self.identifier = identifier

class AreaSetEvent(wx.PyEvent):
    def __init__(self, identifier, area):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_AREA_SET_ID)
        self.identifier = identifier
        self.area = area

class AreaResetEvent(wx.PyEvent):
    def __init__(self, identifier):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_AREA_RESET_ID)
        self.identifier = identifier

class ScreenshotEvent(wx.PyEvent):
    def __init__(self, identifier):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_SCREENSHOT_ID)
        self.identifier = identifier

class ExitEvent(wx.PyEvent):
    def __init__(self, identifier):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_EXIT_ID)
        self.identifier = identifier

class EventScreenAreaWatchdogListener(ScreenAreaWatchdogListener):
    def __init__(self, receiver):
        self.receiver = receiver

    def on_area_changed(self, identifier: int):
        wx.PostEvent(self.receiver, AreaChangedEvent(identifier))

    def on_area_set(self, identifier: int, area: tuple):
        wx.PostEvent(self.receiver, AreaSetEvent(identifier, area))

    def on_area_reset(self, identifier: int):
        wx.PostEvent(self.receiver, AreaResetEvent(identifier))

    def on_screenshot(self, identifier: int):
        wx.PostEvent(self.receiver, ScreenshotEvent(identifier))
        
    def on_exit(self, identifier: int):
        wx.PostEvent(self.receiver, ExitEvent(identifier))

class SelectAreaFrame(wx.Frame):
    def __init__(self, wd: ScreenAreaWatchdog, *args, **kw):
        super(SelectAreaFrame, self).__init__(*args, **kw)
        self.watchdog = wd
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        panel = wx.Panel(self)
        text = "Move and resize panel to the area you want to observe.\nThen simply close this window"
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, label=text), 0, wx.ALL, 4)
        panel.SetSizer(sizer)
        self.EnableCloseButton(True)
        self.EnableFullScreenView(False)
        self.EnableMaximizeButton(False)
        self.EnableMinimizeButton(False)
        if self.CanSetTransparent():
            self.SetTransparent(180)
        self.Center()
        self.Show()

    def OnClose(self, event):
        rect = self.GetRect()
        self.watchdog.set_bbox((rect.GetTopLeft().x, rect.GetTopLeft().y, rect.GetBottomRight().x, rect.GetBottomRight().y))
        self.Destroy()

class ScreenWatchdogFrame(wx.Frame, ScreenAreaWatchdogListener):
    def __init__(self, *args, **kw):
        super(ScreenWatchdogFrame, self).__init__(*args, **kw)
        #self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.shots = 0
        self.disturb = False
        self.watchdog = ScreenAreaWatchdog(EventScreenAreaWatchdogListener(self))
        self.watchdog.rate = 2.0
        panel = wx.Panel(self)
        self.btn_select_area = wx.Button(panel)
        self.btn_select_area.SetLabel('Select area')
        self.btn_select_area.Bind(wx.EVT_BUTTON, self.OnSelectArea)
        self.btn_reset_area = wx.Button(panel)
        self.btn_reset_area.SetLabel('Reset')
        self.btn_reset_area.Hide()
        self.btn_reset_area.Bind(wx.EVT_BUTTON, self.OnReset)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.btn_select_area, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        sizer.Add(self.btn_reset_area, wx.SizerFlags().Center())
        panel.SetSizer(sizer)
        self.CreateStatusBar()
        self.SetStatusText("Select area to watch...")
        self.Center()
        EVT_AREA_CHANGED(self, self.area_changed)
        EVT_AREA_RESET(self, self.area_reset)
        EVT_AREA_SET(self, self.area_set)
        EVT_SCREENSHOT(self, self.screenshot)
        EVT_EXIT(self, self.exit)

    def OnExit(self, event):
        self.watchdog.exit()

    def exit(self, msg):
        self.Close(True)

    def OnSelectArea(self, event):
        self.SetStatusText('Selecting Area now...')
        self.btn_select_area.Hide()
        selectArea = SelectAreaFrame(self.watchdog, None, title='Select Area', size=(400,400))

    def OnReset(self, event):
        self.btn_reset_area.Hide()
        self.watchdog.reset_area()

    def area_changed(self, msg):
        self.on_area_changed(msg.identifier)

    def on_area_changed(self, identifier: int):
        self.SetStatusText('Area changed')
        self.SetBackgroundColour(wx.Colour(255,0,0))
        self.btn_reset_area.Show()
        if self.disturb:
            self.RequestUserAttention()
        else:
            self.ShowWithoutActivating()

    def area_set(self, msg):
        self.on_area_set(msg.identifier, msg.area)

    def on_area_set(self, identifier: int, area: tuple):
        self.watchdog.start()
        self.SetBackgroundColour(wx.Colour(0,255,0))
        self.SetStatusText('Area selected: ' + str(self.watchdog.bbox))

    def area_reset(self, msg):
        self.on_area_reset(msg.identifier)

    def on_area_reset(self, identifier: int):
        self.SetStatusText('Area reset, ready to detect change')
        self.SetBackgroundColour(wx.Colour(0,255,0))

    def screenshot(self,msg):
        self.on_screenshot(msg.identifier)

    def on_screenshot(self, identifier: int):
        self.shots += 1
        self.SetStatusText('Take screenshot...' + str(self.shots))

if __name__ == '__main__':
    app = wx.App()
    frm = ScreenWatchdogFrame(None, title='Screen Watchdog')
    frm.Show()
    app.MainLoop()
