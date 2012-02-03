__all__ = ['TickExtension']

import call_later

class TickExtension(object):
    interval = 1.0
    def onTimer(self):
        "Override this method in your extension class"
        pass
    def _tick(self):
        try:
            self.onTimer()
        finally:
            if self.active:
                call_later.call_later(self._tick, self.interval)
