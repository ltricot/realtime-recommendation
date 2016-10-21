#--external imports
import requests
import sseclient

#--internal imports
from functools import partial
from .testutils import debug
from socket import SHUT_RDWR
import threading
import json


@debug
class ClosableSSEClient(sseclient.SSEClient):

    def __init__(self, *args, **kwargs):
        self.should_connect = True
        super().__init__(*args, **kwargs)

    def _connect(self):
        if self.should_connect:
            super()._connect()
        else:
            raise StopIteration()

    def close(self):
        self.should_connect = False
        self.retry = 0
        self.resp.raw._fp.fp.raw._sock.shutdown(SHUT_RDWR)
        self.resp.raw._fp.fp.raw._sock.close()


@debug
class Stream:

    def __init__(self, url):
        self._url = url

    def start(self, callback):
        url = self._url

        @debug
        class ThreadSSE(threading.Thread):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.client = ClosableSSEClient(url)

            def run(self):
                for event in self.client:
                    if event.event == 'put':
                        event.data = json.loads(event.data)
                        if event.data['path'] == '/': continue
                        event.data['event'] = event.event
                        self._target(event.data)

            def close(self):
                self.client.close()

        self._stream = ThreadSSE(target=callback)
        self._stream.start()

    def close(self):
        if hasattr(self, '_stream'):
            self._stream.close()
            self._stream.join()

    def __del__(self):
        self.close()
