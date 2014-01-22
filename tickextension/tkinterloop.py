# coding: utf-8
__all__ = ['TKInterLoop']

import time

from tickextension.ontickextension import TickExtension

TCL_DONT_WAIT = (1 << 1) # From `tcl.h`

class TKInterLoop(TickExtension):
    """A specialized subclass of TickExtension that will allow the TK event
       loop to run in this extension. Note this will be slightly less
       responsive than tk.mainloop()'s implementation, but it will allow a
       TK user interface to play nicely within ArcMap and friends."""
    _tkinter = None
    interval = 0.125 # Check for events 8 times a second
    def onTimer(self):
        if not self._tkinter:
            import _tkinter
            self._tkinter = _tkinter
        start_time = time.time()
        for event_to_handle in xrange(20):
            ret_val = _tkinter.dooneevent(TCL_DONT_WAIT)
            if ret_val == 0:
                # A return value of 0 means no event was queued for handling,
                # giving us an opportunity to stop handling events for now
                return
            elif (time.time() - start_time) > (self.interval * 0.95):
                # Take a breath if we've spent a long time processing events
                return
