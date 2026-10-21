"""
microdot
--------

The ``microdot`` module defines a few classes that help implement HTTP-based
servers for MicroPython and standard Python.
"""
import asyncio
import io
import re
import time

try:
    import orjson as json
except ImportError:
    import json

try:
    from inspect import iscoroutinefunction, iscoroutine
    from functools import partial

    async def invoke_handler(handler, *args, **kwargs):
        """Invoke a handler and return the result.

        This method runs sync handlers in a thread pool executor.
        """
        if iscoroutinefunction(handler):
            ret = await handler(*args, **kwargs)
        else:
            ret = await asyncio.get_running_loop().run_in_executor(
                None, partial(handler, *args, **kwargs))
        return ret
except ImportError:  # pragma: no cover
    def iscoroutine(coro):
        return hasattr(coro, 'send') and hasattr(coro, 'throw')

    async def invoke_handler(handler, *args, **kwargs):
        """Invoke a handler and return the result.

        This method runs sync handlers in the asyncio thread, which can
        potentially cause blocking and performance issues.
        """
        ret = handler(*args, **kwargs)
        if iscoroutine(ret):
            ret = await ret
        return ret

try:
    from sys import print_exception
except ImportError:  # pragma: no cover
    import traceback

    def print_exception(exc):
        traceback.print_exc()

MUTED_SOCKET_ERRORS = [
    32,  # Broken pipe
    54,  # Connection reset by peer
    104,  # Connection reset by peer
    128,  # Operation on closed socket
]


def urldecode(s):
    if isinstance(s, str):
        s = s.encode()
    s = s.replace(b'+', b' ')
    parts = s.split(b'%')
    if len(parts) == 1:
        return s.decode()
    result = [parts[0]]
    for item in parts[1:]:
        if item == b'':
            result.append(b'%')
        else:
            code = item[:2]
            result.append(bytes([int(code, 16)]))
            result.append(item[2:])
    return b''.join(result).decode()


def urlencode(s):
    return s.replace('+', '%2B').replace(' ', '+').replace(
        '%', '%25').replace('?', '%3F').replace('#', '%23').replace(
            '&', '%26').replace('=', '%3D')


class NoCaseDict(dict):
    """A subclass of dictionary that holds case-insensitive keys.

    :param initial_dict: an initial dictionary of key/value pairs to
                         initialize this object with.

    Example::

        >>> d = NoCaseDict()
        >>> d['Content-Type'] = 'text/html'
        >>> print(d['Content-Type'])
        text/html
        >>> print(d['content-type'])
        text/html
        >>> print(d['CONTENT-TYPE'])
        text/html
        >>> del d['cOnTeNt-TyPe']
        >>> print(d)
        {}
    """
    def __init__(self, initial_dict=None):
        super().__init__(initial_dict or {})
        self.keymap = {k.lower(): k for k in self.keys() if k.lower() != k}

    def __setitem__(self, key, value):
        kl = key.lower()
        key = self.keymap.get(kl, key)
        if kl != key:
            self.keymap[kl] = key
        super().__setitem__(key, value)

    def __getitem__(self, key):
        kl = key.lower()
        return super().__getitem__(self.keymap.get(kl, kl))

    def __delitem__(self, key):
        kl = key.lower()
        super().__delitem__(self.keymap.get(kl, kl))

    def __contains__(self, key):
        kl = key.lower()
        return self.keymap.get(kl, kl) in self.keys()

    def get(self, key, default=None):
        kl = key.lower()
        return super().get(self.keymap.get(kl, kl), default)

    def update(self, other_dict):
        for key, value in other_dict.items():
            self[key] = value


def mro(cls):  # pragma: no cover
    """Return the method resolution order of a class.

    This is a helper function that returns the method resolution order o a
    class. It is used by Microdot to find the best error handler to invoke for
    the raised exception.

    In CPython, this function returns the ``__mro__`` attribute of the class