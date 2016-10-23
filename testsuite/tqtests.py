from functools import wraps
import sys, os, time
import subprocess
import requests


class Env:

    def __init__(self, envars):
        self._envars = envars
        self._env = os.environ.copy()
        self._env.update(envars)

    def __enter__(self):
        self._env, os.environ = os.environ, self._env

    def __exit__(self, *args):
        self._env, os.environ = os.environ, self._env


class PPath(Env):

    def __init__(self, paths):
        self._env = os.environ.copy()
        self._env['PYTHONPATH'] = ':'.join([self._env['PYTHONPATH'], *paths])


def context(manager, *args, **kwargs):
    def manage(func):
        @wraps(func)
        def wrapped(*fargs, **fkwargs):
            with manager(*args, **kwargs):
                results = func(*fargs, **fkwargs)
            return results
        return wrapped
    return manager

with PPath(['/home/loan/MEMETINDER_PROJECT/memetinder-nextgen']):
    p1 = subprocess.Popen(['python', '-m', 'gapis.tqserver', '&'])
    time.sleep(2)
    p2 = subprocess.Popen(['python', '-m', 'testsuite.test2', '&'])
    time.sleep(5)
    p3 = subprocess.Popen(['python', '-m', 'testsuite.test3', '&'])
