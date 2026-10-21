import asyncio
from microdot.helpers import wraps

try:
    import orjson as json
except ImportError:
    import json


class SSE:
    """Server-Sent Events object.

    An object of this class is sent to handler functions to manage the SSE
    connection.
    """
    def __init__(self):
        self.event = asyncio.Event()
        self.queue = []

    async def send(self, data, event=None, event_id=None, retry=None,
                   comment=False):
        """Send an event to the client.

        :param dat: the data to send. It can be given as a string, bytes, dict
                     or list. Dictionaries and lists are serialized to JSON.
                     Any other types are converted to string before sending.
        :param event: an optional event name, to send along with the data. If
                      given, it must be a string.
        :param event_id: an optional event id, to send along with the data. If
                      given, it must be a string.
        :param retry: an optional re