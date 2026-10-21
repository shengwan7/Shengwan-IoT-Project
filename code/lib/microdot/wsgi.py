import asyncio
import os
import signal
from microdot import *  # noqa: F401, F403
from microdot.microdot import Microdot as BaseMicrodot, Request, NoCaseDict, \
    MUTED_SOCKET_ERRORS
from microdot.websocket import WebSocket, websocket_upgrade, \
    with_websocket  # noqa: F401


class Microdot(BaseMicrodot):
    """A subclass of the core :class:`Microdot <microdot.Microdot>` class that
    implements the WSGI protocol.

    This class must be used as the application instance when running under a
    WSGI web server.
    """
    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.embedded_server = False

    def wsgi_app(self, environ, start_response):
        """A WSGI application callable."""
        path = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO', '')
        if 'QUERY_STRING' in environ and environ['QUERY_STRING']:
            path += '?' + environ['QUERY_STRING']
        headers = NoCaseDict()
       content_length = 0
        for k,