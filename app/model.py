"""
    Goal of this module: Implement recommender models capable of handling
realtime updates -- that is, frequent updates to only part of a model.

"""


#--internal imports
from . import skeleton
from .testutils import debug

#--built-in imports
from collections import namedtuple

#--external imports
import numpy as np


#--code
gradient = namedtuple('gradient', ['user', 'item', 'biases'])
# TO-DO user & item separated bias gradients ^. Actually not necessarily
vecbi = namedtuple('item', ['vector', 'bias'])


@debug
class MatFac(skeleton.Model):

    def __init__(self, eta):
        self._eta = eta

    def _grad(self, user, item, data):
        grad = self._eta * (self.suggest(user, item) - data)
        return gradient(
            user=np.mean(item.vector * grad), # multiple items
            item=user.vector * grad,
            biases=grad)

    def update(self, user, item, data):
        grad = self._grad(user, item, data)
        user = vecbi(
            vector=user.vector - grad.user,
            bias=user.bias - np.mean(grad.biases)) # multiple items
        item = vecbi(
            vector=item.vector - grad.item,
            bias=item.bias - grad.biases)
        return user, item

    def suggest(self, user, item):
        return np.dot(user.vector, item.vector.T) + user.bias + item.bias

    def test(self):
        pass
