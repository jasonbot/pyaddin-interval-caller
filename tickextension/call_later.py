import collections
import ctypes
import ctypes.wintypes
import time
import traceback

import streamwrapper

try:
    import pythonaddins
    def printfunc(message, error=False):
        try:
            pythonaddins._WriteStringToPythonWindow(message, True, True, error)
        except:
            print message
except:
    def printfunc(message, error=False):
        print message

__all__ = ['call_later']

callback_type = ctypes.WINFUNCTYPE(None,
                                   ctypes.wintypes.HWND,
                                   ctypes.wintypes.UINT,
                                   ctypes.POINTER(ctypes.wintypes.UINT),
                                   ctypes.wintypes.DWORD)

settimer = ctypes.windll.user32.SetTimer
settimer.restype = ctypes.POINTER(ctypes.wintypes.UINT)
settimer.argtypes = [ctypes.wintypes.HWND,
                     ctypes.POINTER(ctypes.wintypes.UINT),
                     ctypes.wintypes.UINT,
                     callback_type]

killtimer = ctypes.windll.user32.KillTimer
killtimer.restype = ctypes.wintypes.BOOL
killtimer.argtypes = [ctypes.wintypes.HWND,
                      ctypes.POINTER(ctypes.wintypes.UINT)]

WM_TIMER = 0x0113

class CallQueue(object):
    """Represents a queue of function calls that will be executed in this
       thread's Win32 message loop."""
    _fraction = 1 # Accurate to 10**_fraction of a second
    def __init__(self):
        self._queued_functions = collections.defaultdict(list)
        self._call_later_callback = callback_type(self._callback_handler)
        self._timerid = None
        self._active = False
    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, val):
        if val and not self._active:
            self._timerid = settimer(0, # NULL HWND
                                     self._timerid,
                                     int(10**-self._fraction * 1000),
                                     self._call_later_callback)
            self._active = True
            return
        elif (not val) and self._active:
            self._active = (killtimer(0, self._timerid) != 0)
            return
        self._active = bool(val)
    def call_later(self, callable, delay_in_seconds=1):
        """Allows a callable object to be executed later in a Windows
           application.

           Example:

           def update():
               print 'Hello!'

           call_later.call_later(update, 10) # Will print "Hello!" in 10 sec
        """
        later = round(time.time() + delay_in_seconds, self._fraction)
        if isinstance(callable, (list, tuple)):
            for c in callable:
                self._queued_functions[str(later)].append(c)
        else:
            self._queued_functions[str(later)].append(callable)
        self.active = True
        return id(callable)
    def _callback_handler(self, hwnd, uMsg, idEvent, dwTime):
        #printfunc("Calling WM_TIMER callback {}, {}, {}, {}"
        #          .format(hwnd, uMsg, idEvent, dwTime))
        try:
            self._flush(True)
        except Exception as e:
            # printfunc(traceback.format_exc().rstrip(), True)
            pass
    def _flush(self, update=True):
        flush_time = round(time.time(), self._fraction)
        keys = set(t for t in self._queued_functions
                   if float(t) <= flush_time)
        #printfunc("Flushing keys: {}".format(keys))
        for key in sorted(keys):
            with streamwrapper.wrapped_streams:
                for fn in self._queued_functions[key]:
                    #printfunc("Calling {} - {}".format(key, fn))
                    try:
                        if id(fn) in self._cancel_list:
                            self._cancel_list.remove(id(fn))
                        else:
                            fn()
                    except Exception as e:
                        #pass
                        printfunc(traceback.format_exc().rstrip(), True)
        for key in keys:
            del self._queued_functions[key]
        if not self._queued_functions:
            self.active = False

call_queue = CallQueue()
call_later = call_queue.call_later
cancel_call = call_queue.cancel_call
