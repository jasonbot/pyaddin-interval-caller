__all__ = ['wrapped_streams']

import sys

import pythonaddins

class StreamWrapper(object):
    def __init__(self, original):
        self._original = original
        self._buffer = u""
    def write(self, *args, **kwargs):
        try:
            self._buffer += u' '.join(a.decode("utf-8", "replace")
                                        if isinstance(a, basestring)
                                        else unicode(repr(a))
                                      for a in args)
        except:
            pass
        if '\n' in self._buffer:
            outstring, self._buffer = self._buffer.rsplit('\n', 1)
            try:
                pythonaddins._WriteStringToPythonWindow(outstring)
            except:
                return self._original.write(*args, **kwargs)
    def finalize(self):
        if self._buffer:
            self.write('\n')
    def __getattr__(self, attrname):
        if attrname not in ('write', 'finalize'):
            return getattr(self._original, attrname)

class StreamWrapperContextManager(object):
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = StreamWrapper(sys.stdout)
        sys.stderr = StreamWrapper(sys.stderr)
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.finalize()
        sys.stderr.finalize()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

wrapped_streams = StreamWrapperContextManager()
