"""
    Module's goal is to build a recommendation system for suggesting memes to
users. The model will use data given explicitly by the user (likes and
dislikes) to build recommendations.

    The final recommender class will be built by inheriting from all classes
which bring desired functionality to the system. The classes below are mix-ins
and are therefore not all necessary; when building the final class, make sure
the inheritance order (which determines the method resolution order, or `MRO`)
is right (or use the `Build` metaclass), so that all classes manage to get the
right arguments when their methods are called.

"""


#--internal imports
from .stream import Stream
from .testutils import debug
from .model import *
from . import skeleton

#--built-in imports
import base64
import struct
import json
import abc

#--external imports
from firebase import firebase
import numpy as np

# from google.appengine.api import taskqueue # this works in python 2
from gapis import tqclient as taskqueue


#--code...
@debug
class FBSystem(skeleton.System):
    """
        Obsolete. Testing purposes.

    """

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
            ubias, ibias = map(float, (ubias, ibias))

            user, item = self.update(
                vecbi(user, ubias),
                vecbi(item, ibias),
                event['data'])

            self.export(username, user, itemname, item)
        self._stream.start(handle)

    def export(self, username, user, itemname, item):
        uvec, ivec = self._coder.encode(user.vector, item.vector)
        user = str(user.bias) + '_' + uvec
        item = str(item.bias) + '_' + ivec

        self._firebase.put('/vectors/users', username, user)
        self._firebase.put('/vectors/memes', itemname, item)

    def parse(self):
        pass


@debug
class QueuedFBSystem:

    def __init__(self, queue, url, *args, **kwargs):
        self._stream = Stream(url + 'likes.json')
        self._queue = queue
        super().__init__(*args, **kwargs)

    def fetch(self):
        def handle(event):
            path = event['path']
            if path.startswith('/'): path = path[1:]
            username, itemname = path.split('/')
            payload = json.dumps({'meme': itemname, 'data': event['data']})
            self._queue.add([taskqueue.Task(
                payload=payload,
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



@debug
class Build(abc.ABCMeta):
    """
        Specify this metaclass if you don't want to have to deal with mix-in
    inheritance order. Do it. Really.

    """

    def __new__(mcls, name, bases, dictionary):
        return super().__new__(mcls, name,
            tuple(sorted(bases, key=lambda cls: -cls.key)),
            dictionary)
