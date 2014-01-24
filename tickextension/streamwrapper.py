__all__ = ['wrapped_streams']

import sys

try:
    import pythonaddins
except ImportError:
    class pythonaddins(object):
        @staticmethod
        def _WriteStringToPythonWindow(out_string,
                                       reprompt_when_done=True,
                                       is_error=False):
            pass

class StreamWrapper(object):
    def __init__(self, wrapped_stream, stderr=False):
        self._wrapped_stream = wrapped_stream
        self._buffer = u""
        self._stderr = stderr
        self._reprompt = False
        self._wroteout = False
    def write(self, *args, **kwargs):
        try:
            self._buffer += u' '.join(a.decode("utf-8", "replace")
                                        if isinstance(a, basestring)
                                        else unicode(repr(a))
                                      for a in args)
        except:
            pass
        if self._buffer:
            self._wroteout = True
        if '\n' in self._buffer:
            outstring, self._buffer = self._buffer.rsplit('\n', 1)
            try:
                outstring = (outstring.replace('\r\n', '\n')
                                      .replace('\n', '\r\n'))
                pythonaddins._WriteStringToPythonWindow(outstring,
                                             reprompt_when_done=self._reprompt,
                                             is_error=self._stderr)
            except:
                return self._wrapped_stream.write(*args, **kwargs)
    def flush(self):
        self._wrapped_stream.flush()
    def finalize(self, reprompt=False):
        self._reprompt = reprompt
        if self._buffer and isinstance(self._buffeer, unicode):
            pythonaddins._WriteStringToPythonWindow(self._buffer,
                                         reprompt_when_done=self._reprompt,
                                         is_error=self._stderr)
            self._wroteout = True
            self.write(self.buffer)
        elif self._reprompt:
            pythonaddins._WriteStringToPythonWindow(u"",
                                         reprompt_when_done=True,
                                         is_error=self._stderr)
    @property
    def printed(self):
        return self._wroteout
    def __getattr__(self, attrname):
        if attrname not in ('write', 'finalize'):
            return getattr(self._wrapped_stream, attrname)

class StreamWrapperContextManager(object):
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = StreamWrapper(sys.stdout)
        sys.stderr = StreamWrapper(sys.stderr, True)
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.finalize()
        sys.stderr.finalize()
        printed = (getattr(sys.stdout, 'printed', False) or
                   getattr(sys.stderr, 'printed', False))
        # Reprompt if anything had printed out
        if printed:
            pythonaddins._WriteStringToPythonWindow(u"",
                                                    reprompt_when_done=True)
        sys.stdout = self._stdout
        sys.stderr = self._stderr

wrapped_streams = StreamWrapperContextManager()
