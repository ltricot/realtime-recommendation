from google.appengine.api import taskqueue
import grequests
import skeleton


class Worker:

    def __init__(self, system, queue, firebase, encoder):
        self.firebase = firebase
        self.system = system
        self.queue = queue
        self.coder = encoder

    async def run(self):
        while True:
            tasks = self.queue.lease_tasks_by_tag(
                lease_seconds=30,
                max_tasks=50,
                deadline=5)

            username = tasks[0].tag
            itemnames = (task.payload for task in tasks)

            items = []
            ubias, user = self.firebase.get('/vectors/users', username).split('_')
            for itemname in itemnames:
                self.firebase.get_async(
                    '/vectors/memes', itemname,
                    lambda s: items.append(tuple(s.split('_'))))

            await (items, len(tasks))
            items, ibiases = list(zip(*items))
            user, *items = self.coder.decode(user, *items)
            ubias, *ibiases = map(float, (ubias, *ibiases))

            user, item = self.system.update(
                vecbi(user, ubias),
                vecbi(items, ibiases),
                event['data'])

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
