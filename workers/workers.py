"""
    For now this module uses the python-firebase library. Will have to dump it
because of crappy async handling -- it uses multiprocessing... Will move to the
requests and grequests library. This is done now.

"""


from app import skeleton
from app.model import vecbi

# from google.appengine.api import taskqueue # this works in python 2
from gapis import tqclient as taskqueue

import numpy as np
import grequests # incompatible with sseclient bc/ of gevent
import requests
import json


class Worker:

    def __init__(self, system, queue, url, encoder):
        self.url = url
        self.system = system
        self.queue = queue
        self.coder = encoder

    def run(self):
        while True:
            tasks = self.queue.lease_tasks_by_tag(
                lease_seconds=30,
                max_tasks=50,
                deadline=5)

            username = tasks[0].tag
            payloads = (json.loads(task.payload) for task in tasks)
            itemnames, results = tuple(
                zip(*((p['meme'], p['data']) for p in payloads)))

            ubias, user = requests.get(
                self.url + 'vectors/users/' + username + '.json').json().split('_')

            reqs = (grequests.get(
                self.url + 'vectors/memes/' + i + '.json') for i in itemnames)
            ibiases, items = tuple(zip(
                *(r.json().split('_') for r in grequests.map(reqs) if r != None)))

            user, *items = self.coder.decode(user, *items)
            ubias, *ibiases = map(float, (ubias, *ibiases))

            user, item = self.system.update(
                vecbi(user, ubias),
                vecbi(np.array(items), np.array(ibiases)),
                np.array([results]).T)

            uservec, *itemvecs = self.coder.encode(user.vector, *list(item.vector))
            reqs = (grequests.patch(self.url + 'vectors/memes/.json', data=json.dumps(
                {i: str(ib) + '_' + iv})) for i, ib, iv in zip(itemnames, item.bias.T[0], itemvecs))
            grequests.map(reqs)
            requests.patch(self.url + 'vectors/users/.json', data=json.dumps(
                {username: str(user.bias) + '_' + uservec}))

            self.queue.delete_tasks(tasks)
