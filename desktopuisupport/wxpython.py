import call_later
import wx

class WXEventLoop(object):
    _interval = 0.05
    def __init__(self):
        self._running = False
        self._oldloop = None
        self._eventloop = wx.EventLoop()
        self.start()
    def start(self):
        self._running = True
        self._oldloop = wx.EventLoop.GetActive()
        wx.EventLoop.SetActive(self._eventloop)
        call_later.call_later(self.tick, self._interval)
    def stop(self):
        self._running = False
    def tick(self):
        while self._eventloop.Pending():
            self._eventloop.Dispatch()
        if self._running:
            call_later.call_later(self.tick, self._interval)
        else:
            wx.EventLoop.SetActive(self._oldloop)

wx_app = wx.App(0)
wx_loop = WXEventLoop()
