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
    def __init__(self):
        self._queued_functions = collections.defaultdict(list)
        self._call_later_callback = callback_type(self._callback_handler)
        self._timerid = None
    def call_later(self, callable, delay_in_seconds=1):
        """Allows a callable object to be executed later in a Windows
           application.
           
           Example:
               
           def update():
               print 'Hello!'
           
           call_later.call_later(update, 10) # Will print "Hello!" in 10 sec
        """
        self._flush()

        need_update = False
        assert delay_in_seconds >= 1, \
               "Delay of {} seconds is not valid".format(delay_in_seconds)
        later = time.time() + delay_in_seconds
        if not self._queued_functions:
            need_update = True
        elif later <= int(min(self._queued_functions)):
            need_update = True
        if isinstance(callable, (list, tuple)):
            for c in callable:
                self._queued_functions[later].append(c)
        else:
            self._queued_functions[later].append(callable)
        #printfunc("Queued funtion {} and I am {}"
        #          .format(callable, self._queued_functions))
        if need_update:
            self._update()
        return id(callable)
    def cancel_call(self, function_id):
        """Cancels all outstanding scheduled calls to the provided function id
           as returned from call_later"""
        keys_to_kill = [k for k in self._queued_functions 
                        if id(id) in map(self._queued_functions[k])]
        for key in keys_to_kill:
            self._queued_functions[key] = [item
                                           for item in 
                                             self._queued_functions[key]
                                           if id(item) != function_id]
        if keys_to_kill:
            self._update()
    def _update(self):
        #printfunc("Updating")
        if self._queued_functions:
            if min(self._queued_functions) < time.time():
                self._flush(time.time(), False)
            if self._queued_functions:
                mt = min(self._queued_functions)
                # +10 mS fudge factor
                callback_time = max([20,
                                     int(((mt - time.time()) * 1000) + 10)])
                #printfunc("Need update! Setting timer for {} ms ({})"
                #          .format(callback_time, mt))
                self._timerid = settimer(0, # NULL HWND
                                         self._timerid,
                                         callback_time,
                                         self._call_later_callback)
        if not self._queued_functions:
            killtimer(0, self._timerid)
    def _callback_handler(self, hwnd, uMsg, idEvent, dwTime):
        #printfunc("Calling WM_TIMER callback {}, {}, {}, {}"
        #          .format(hwnd, uMsg, idEvent, dwTime))
        try:
            now = int(time.time())
            self._flush(now, True)
        except Exception as e:
            printfunc(traceback.format_exc().rstrip(), True)
    def _flush(self, flush_time=None, update=True):
        if flush_time is None:
            flush_time = int(time.time())
        keys = [t for t in self._queued_functions if t <= flush_time]
        #printfunc("Flushing keys: {}".format(keys))
        for key in keys:
            for fn in self._queued_functions[key]:
                #printfunc("Calling {}".format(fn))
                try:
                    fn()
                except Exception as e:
                    printfunc(traceback.format_exc().rstrip(), True)
            del self._queued_functions[key]
        if update:
            self._update()

call_queue = CallQueue()
call_later = call_queue.call_later
cancel_call = call_queue.cancel_call
