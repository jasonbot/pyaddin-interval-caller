import collections
import ctypes
import ctypes.wintypes
import time
import traceback

try:
    import pythonaddins
    pythonaddins._WriteStringToPythonWindow("", False, True, False)
    def printfunc(message, error=False):
        pythonaddins._WriteStringToPythonWindow(message, True, True, error)
except:
    def printfunc(message, error=False):
        print message

__all__ = ['call_later', 'cancel_call']

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
        self._cancel_list = set()
        self._timerid = settimer(0, # NULL HWND
                                 self._timerid,
                                 int(10**-self._fraction * 1000),
                                 self._call_later_callback)
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
        return id(callable)
    def cancel_call(self, function_id):
        """Cancels all outstanding scheduled calls to the provided function id
           as returned from call_later"""
        if not isinstance(function_id, (int, long)):
            function_id = id(function_id)
        self._cancel_list.add(function_id)
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

call_queue = CallQueue()
call_later = call_queue.call_later
cancel_call = call_queue.cancel_call
