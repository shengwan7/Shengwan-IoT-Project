import binascii
import hashlib
from microdot import Request, Response
from microdot.microdot import MUTED_SOCKET_ERRORS, print_exception
from microdot.helpers import wraps


class WebSocketError(Exception):
    """Exception raised when an error occurs in a WebSocket connection."""
    pass


class WebSocket:
    """A WebSocket connection object.

    An instance of this class is sent to handler functions to manage the
    WebSocket connection.
    """
    CONT = 0
    TEXT = 1
    BINARY = 2
    CLOSE = 8
    PING = 9
    PONG = 10

    #: Specify the maximum message size that can be received when calling the
    #: ``receive()`` method. Messages with payloads that are larger than this
    #: size will be rejected and the connection closed. Set to 0 to disable
    #: the size check (be aware of potentil security issues if you do this),
    #: or to -1 to use the value set in
    #: ``Request.max_body_length``. The default is -1.
    #:
    #: Example::
    #:
    #:    WebSocket.max_message_length = 4 * 1024