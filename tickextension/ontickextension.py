# coding: utf-8
__all__ = ['TickExtension']

import call_later

class TickExtension(object):
    """An inheritable class for Python Add-In Extensions that will call
       self.onTimer() at regular intervals. Please refer to the
       documentation in README.md for usage."""
    interval = 1.0
    def onTimer(self):
        "Override this method in your extension class"
        pass
    def startup(self):
        self.startTimer()
    def startTimer(self):
        if getattr(self, 'interval', None):
            call_later.call_later(self._tick, self.interval)
        else:
            call_later.cancel_call(self._tick)
    def _tick(self):
        try:
            self.onTimer()
        finally:
            if getattr(self, 'enabled', False) and getattr(self, 'interval', None):
                call_later.call_later(self._tick, self.interval)
