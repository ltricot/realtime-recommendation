"""
    Machine learning models such as Matrix Factorization and Restricted
Boltzmann Machines. (The latter is a work in progress). These are the kernels
of the suggest system, all other classes are built around those to ease their
use.

"""


#--internal imports
from testutils import TESTING
import skeleton

#--built-in imports
from warnings import warn
import random
import abc

#--external imports
from scipy.spatial.distance import cdist
import numpy as np

rng = np.random


#--code...
class MatrixFactorization(skeleton.Model):
    """
        Matrix Factorization is a model-based technique for recommender systems
    which infers user and item profiles given user item interactions, and uses
    those profiles to recommend items to users. The model is much more
    expressive than a neighborhood model because user and item profiles are
    influenced by all direct and indirect relationships with both other users
    and other items. This model has the additional benefit of creating data
    which can have uses outside of recommendation. (Document or user clustering
    based on the profiles inferred, for example).

    """
    key = 1
    maxiter = 200

    def __init__(self, *, nb_users, nb_items, vector_size=20):
        self._users = np.random.normal(size=(nb_users, vector_size))
        self._items = np.random.normal(size=(nb_items, vector_size))

        self._u_biases = np.zeros(nb_users)
        self._i_biases = np.zeros(nb_items)
        self._bias = 0

    def update(self, *args, **kwargs):
        """
            This method invokes the SGD method which handles the training of the
        model. Simple as that.

        """
        self._SGD(*args, **kwargs)

    def _SGD(self, data, epochs=None, lmbda=0, eta=2):
        """
            Gradient descent.
        Since this model is linear, gradient descent is simple:
        The gradient for the user is the the loss function's gradient with
        respect to the model's result, multiplied by the item. Same goes for the
        item (however this time multiplied by the user).

            We train on all elements of the user_item_matrix which are non zero,
        treating elements equal to zero as missing data. The goal is to be able
        to fill that missing data with the knowledge acquired from the given
        data. One can recommend using the filled missing data (if the model
        thinks a user should see a document, the user's vector multiplied by the
        document's vector will give a big result relative to other
        multiplications).

        """
        global TESTING

        self._UIM = data
        self.eta = eta
        if epochs is None:
            iters = self.maxiter
        else:
            iters = epochs

        costs = []
        indices = list(zip(*data.nonzero()))
        for e in range(iters):
            random.shuffle(indices)
            for i, j in indices:
                self._grad_update(i, j, lmbda)

            costs.append(self.test(self._UIM))
            costs = costs[-20:]

            if len(costs) == 20 and epochs is None:
                if np.mean(np.asarray(costs[:-1]) - np.asarray(costs[1:])) < 0:
                    break

            if TESTING:
                print(costs[-1])

    def _grad_update(self, i, j, lmbda):
        """
            Calculates cost function's gradient with respect to the model's
        results. Cutting the SGD functionality in multiple methods helps in
        defining mix-ins for different weight update rules and other
        regularisation methods.

        """

        user, item = self._users[i], self._items[j]
        result = user.dot(item) + self._bias + self._u_biases[i] + self._i_biases[j]
        grad = (result - self._UIM[i, j])

        if np.isnan(grad):
            raise ArithmeticError

        self._update_weights(grad, i, j, lmbda, user, item)

    def _update_weights(self, grad, i, j, lmbda, user, item):
        """
            Like above. This method does the actual updating of the weights.

        """

        grad = self.eta * grad
        self._u_biases -= grad
        self._i_biases -= grad
        self._bias -= grad

        self._users[i] -= grad * item + lmbda * user**2
        self._items[j] -= grad * user + lmbda * item**2

    def suggest(self, users=None):
        """
            Takes a list of indices. Returns recommendation for all users
        pointed to by the indices. If users is None, returns suggestions for
        all users.

        """

        if users is None: return self._users.dot(self._items.T) + self._u_biases[:, np.newaxis] \
                         + self._i_biases + self._bias
        return self._users[users].dot(self._items.T) + self._u_biases[users, np.newaxis] \
               + self._i_biases + self._bias

    def test(self, truth):
        """
            Returns Mean Squared Error on given data.

        """

        indices = truth.nonzero()
        results = MatrixFactorization.suggest(self)
        return ((results[indices] - truth[indices])**2).mean()


class AdaGradMF(MatrixFactorization):
    """
        Automatically adapts the learning rate in a per-dimension way. Learning
    becomes more effective, more consistent and considerably faster.

    """
    key = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._u_historical = np.zeros(self._users.shape)
        self._i_historical = np.zeros(self._items.shape)
        self._b_hist = 0

    def _update_weights(self, grad, i, j, lmbda, user, item):
        """
            A bunch of math stuff. Divides the gradient by the norm of the
        history of all gradients before this one.

        """

        u_grad, i_grad = item * grad, user * grad
        self._u_historical[i] += u_grad**2
        self._i_historical[j] += i_grad**2
        self._b_hist += grad**2

        u_sqrt = np.sqrt(self._u_historical[i])
        i_sqrt = np.sqrt(self._i_historical[j])
        u_grad = self.eta * u_grad / (1e-10 + u_sqrt)
        i_grad = self.eta * i_grad / (1e-10 + i_sqrt)

        self._users[i] -= u_grad + self.eta * (lmbda / (1e-10 + u_sqrt)) * user**2
        self._items[j] -= i_grad + self.eta * (lmbda / (1e-10 + i_sqrt)) * item**2

        grad = self.eta * grad / (1e-10 + np.sqrt(self._b_hist))
        self._u_biases[i] -= grad
        self._i_biases[j] -= grad
        self._bias -= grad


class Dropout(MatrixFactorization):
    """
        Adapted regularization method from neural nets. Gives surprisingly good
    results.

    """
    key = 3

    def update(self, p=0.7, *args, **kwargs):
        self.p = p
        super().update(*args, **kwargs)

    def _grad_update(self, i, j, lmbda):
        """
            Simply drops out certain elements of the user and item vectors (the
        same indices are used for both) hoping that it will prevent the features
        described by those elements from adapting to the presence of other
        features.

        """

        mask = rng.binomial(
            n=1, size=self._users.shape[1], p=self.p)
        user, item = self._users[i]*mask, self._items[j]*mask
        result = user.dot(item) + self._bias + self._u_biases[i] + self._i_biases[j]
        grad = (result - self._UIM[i, j])

        if np.isnan(grad):
            raise ArithmeticError

        self._update_weights(grad, i, j, lmbda, user, item)

    def suggest(self, *args, **kwargs):
        """
            Since we dropped out a certain number of elements each time we
        trained, we need to compensate for the fact that the not-dropped out
        elements adapted themselves to be fewer, and therefore needed to get
        bigger. We now use all the elements, so divide them.

        """

        return super().suggest(*args, **kwargs) * self.p
