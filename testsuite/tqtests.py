from functools import wraps
import sys, os, time
import subprocess
import requests
import json


URL = 'https://meme-tinder.firebaseio.com/'

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

with PPath(['/home/loan/MEMETINDER_PROJECT/memetinder-nextgen']), open('/dev/null', 'w') as void:
    p1 = subprocess.Popen(['python', '-m', 'gapis.tqserver', '&'])
    p2 = subprocess.Popen(['python', '-m', 'testsuite.test2', '&'])
    p3 = subprocess.Popen(['python', '-m', 'testsuite.test3', '&'])

def overload():
    n = 1; name1 = 'loan'; name2 = 'simon'
    for x in range(100):
        if x % 4 == 0:
            n = -n
            name1, name2 = name2, name1
        data = json.dumps({'meme{}'.format((x % 4) + 1): n})
        requests.patch(
            URL + 'likes/{}/.json'.format(name1),
            headers=headers,
            data=data)

overload()
