"""
    For now this module uses the python-firebase library. Will have to dump it
because of crappy async handling -- it uses multiprocessing... Will move to the
requests and grequests library.

"""


from . import skeleton

from google.appengine.api import taskqueue
import grequests
import json


class Worker:

    def __init__(self, system, queue, firebase, encoder):
        self.url = firebase
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
            itemnames, results = tuple(zip(*(p['meme'], p['data'] for p in payloads)))

            ubias, user = requests.get(
                self.url + 'vectors/users/' + username).split('_')

            reqs = (grequests.get(self.url + 'vectors/memes/' + i) for i in itemnames)
            ibiases, items = tuple(zip(
                *(r.json().split('_') for r in grequests.map(reqs) if r != None)))

            user, *items = self.coder.decode(user, *items)
            ubias, *ibiases = map(float, (ubias, *ibiases))

            user, item = self.system.update(
                vecbi(user, ubias),
                vecbi(np.array(items), np.array(ibiases)),
                np.array([results]).T)

            self.queue.delete_tasks(tasks)


class Boss:
    """
        Manages a group of workers.

    """

    def __init__(self, workers):
        self.workers = workers

    def run(self):
        # manages workers run coroutines.
        running = {worker.run(): None for worker in self.workers}
        while True:
            for worker, item in running.items:
                if item is not None:
                    lis, leng = item
                    if len(lis) != leng:
                        continue
                running[worker] = worker.send(None)
