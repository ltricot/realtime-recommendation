"""
    Testing context utilities.

"""

from functools import wraps
import sys, os


class Env:

    def __init__(self, envars):
        self._envars = envars
        self._env = os.environ.copy()
        self._env.update(envars)

    def __enter__(self):
        self._env, os.environ = os.environ, self._env

    def __exit__(self, *args):
        self._env, os.environ = os.environ, self._env


class PythonPath(Env):

    def __init__(self, paths):
        self._env = os.environ.copy()
        self._env['PYTHONPATH'] = ':'.join([self._env['PYTHONPATH'], *paths])


def context(manager):
    def manage(func):
        @wraps(func)
        def wrapped(*fargs, **fkwargs):
            with manager:
                results = func(*fargs, **fkwargs)
            return results
        return wrapped
    return manager
