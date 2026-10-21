import os
from random import choice
from microdot import abort, iscoroutine, AsyncBytesIO
from microdot.helpers import wraps


class FormDataIter:
    """Asynchronous iterator that parses a ``multipart/form-data`` body and
    returns form fields and files as they are parsed.

    :param request: the request object to parse.

    Example usage::

        from microdot.multipart import FormDataIter

        @app.post('/upload')
        async def upload(request):
            async for name, value in FormDataIter(request):
                print(name, value)

    The iterator returns no values when the request has a content type other
    than ``multipart/form-data``. For a file field, the returned value is of
    type :class:`FileUpload`, which supports the
    :meth:`read() <FileUpload.read>` and :meth:`save() <FileUpload.save>`
    methods. Values for regular fields are provided as strings.

    The request body is read efficiently in chunks of size
    :attr:`buffer_size <FormDataIter.buffer_size>`. On iterations in which a
    file field is encountered, the file must be consumed before moving on to
    the next iteration, as the internal stream stored in ``FileUpload``
    instances is invalidated at the end of the iteration.
    """
    #: The size of the buffer used to read chunks of the request body. This
    #: size must be large enough to hold at least one complete header or
    #: boundary line, so it is not recommended to lower it, but it can be made
    #: higher to improve performance at the expense of RAM.
    buffer_size = 256

    def __init__(self, request):
        self.request = request
        self.buffer = None
        try:
            mimetype, boundary = request.content_type.rsplit('; boundary=', 1)
        except ValueError:
            return  # not a multipart request
        if mimetype.split(';', 1)[0] == \
                'multipart/form-data':  # pragma: no branch
            self.boundary = b'--' + boundary.encode()
            self.extra_size = len(boundary) + 4
            self.buffer = b''

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.buffer is None:
            raise StopAsyncIteration

        # make sure we have consumed the previous entry
        while await self._read_buffer(self.buffer_size) != b'':
            pass

        # make sure we are at a boundary
        await self._fill_buffer()
        s = self.buffer.split(self.boundary, 1)
        if len(s) != 2 or s[0] != b'':
            abort(400)  # pragma: no cover
        self.buffer = s[1]
        if self.buffer[:2] == b'--':
            # we have reached the end
            raise StopAsyncIteration
        elif self.buffer[:2] != b'\r\n':
            abort(400)  # pragma: no cover
        self.buffer = self.buffer[2:]

        # parse the headers of this part
        name = ''
        filename = None
        content_type = None
        while True:
            await self._fill_buffer()
            lines = self.buffer.split(b'\r\n', 1)
            if len(lines) != 2:
                abort(400)  # pragma: no cover
            line, self.buffer = lines
            if line == b'':
                # we reached the end of the headers
                break
            header, value = line.decode().split(':', 1)
            header = header.lower()
            value = value.strip()
            if header == 'content-disposition':
                parts = value.split(';')
                if len(parts) < 2 or parts[0] != 'form-data':
                    abort(400)  # pragma: no cover
                for part in parts[1:]:
                    part = part.strip()
                   if part.startswith('name="'):
                        name = part[6:-1]
                    elif part.startswith('filename="'):  # pragma: no branch
                        filename = part[10:-1]
            elif header == 'content-type':  # pragma: no branch
                content_type = value

        if filename is None:
            # this is a regular form field, so we read the value
            value = b''
      