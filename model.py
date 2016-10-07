"""
    Goal of this module: Implement recommender models capable of handling
realtime updates -- that is, frequesnt updates to only part of a model.

"""


#--internal imports
import skeleton
from stream import Stream
from testutils import debug

#--built-in imports
from collections import namedtuple
import base64
import struct

#--external imports
import numpy as np
from firebase import firebase
from google.appengine.api import taskqueue


#--code
gradient = namedtuple('gradient', ['user', 'item', 'biases'])
vecbi = namedtuple('item', ['vector', 'bias'])


@debug
class MatFac(skeleton.Model):

    def __init__(self, eta):
        self._eta = eta

    def _grad(self, user, item, data):
        grad = self._eta * (self.suggest(user, item) - data)
        return gradient(
            user=item.vector * grad,
            item=user.vector * grad,
            biases=grad)

    def update(self, user, item, data):
        grad = self._grad(user, item, data)
        user = vecbi(
            vector=user.vector - grad.user,
            bias=user.bias - grad.biases)
        item = vecbi(
            vector=item.vector - grad.item,
            bias=item.bias - grad.biases)
        return user, item

    def suggest(self, user, item):
        return np.dot(user.vector, item.vector) + user.bias + item.bias

    def test(self):
        ...


@debug
class FBSystem(skeleton.System):

    def __init__(self, url, coder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stream = Stream(url + 'likes.json')
        self._firebase = firebase.FirebaseApplication(url, None)
        self._coder = coder

    def fetch(self):
        def handle(event):
            # In the future this will send a task on a pull queue.
            # Workers will lease tasks to preform batched updates

            path = event['path']
            if path.startswith('/'): path = path[1:]
            username, itemname = path.split('/')

            ubias, user = self._firebase.get('/vectors/users', username).split('_')
            ibias, item = self._firebase.get('/vectors/memes', itemname).split('_')
            user, item = self._coder.decode(user, item)
            ubias, ibias = float(ubias), float(ibias)

            user, item = self.update(
                vecbi(user, ubias),
                vecbi(item, ibias),
                event['data'])

            self.export(user, item)

        self._stream.start(handle)

    def export(self, user, item):
        uvec, ivec = self._coder.encode(user.vector, item.vector)
        user = str(user.bias) + '_' + uvec
        item = str(item.bias) + '_' + ivec

        self._firebase.put('/vectors/users', username, user)
        self._firebase.put('/vectors/memes', itemname, item)

    def parse(self):
        ...


@debug
class QueuedFBSystem(FBSystem):

    def __init__(self, queue, *args, **kwargs):
        self._queue = queue
        super().__init__(*args, **kwargs)

    def fetch(self):
        def handle(event):
            path = event['path']
            if path.startswith('/'): path = path[1:]
            username, itemname = path.split('/')
            self._queue.add([taskqueue.Task(
                payload=itemname,
                tag=username,
                method='PULL')])
        self._stream.start(handle)


@debug
class Encoder:

    @staticmethod
    def encode(*args):
        args = (struct.pack('f'*len(arg), *arg) for arg in args)
        return [base64.b64encode(arg).decode() for arg in args]

    @staticmethod
    def decode(*args):
        args = (base64.b64decode(arg) for arg in args)
        return [np.array(struct.unpack('f'*(len(arg)//4), arg)) for arg in args]
