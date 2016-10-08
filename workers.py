from google.appengine.api import taskqueue
import grequests
import skeleton


class Worker:

    def __init__(self, system, queue, firebase, encoder):
        self.firebase = firebase
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
            itemnames = (task.payload for task in tasks)

            items = []
            ubias, user = self.firebase.get('/vectors/users', username).split('_')
            for itemname in itemnames:
                self.firebase.get_async(
                    '/vectors/memes', itemname,
                    lambda s: items.append(tuple(s.split('_'))))

            items, ibiases = list(zip(*items))
            user, *items = self.coder.decode(user, *items)
            ubias, *ibiases = map(float, (ubias, *ibiases))

            user, item = self.system.update(
                vecbi(user, ubias),
                vecbi(items, ibiases),
                event['data'])

            self.queue.delete_tasks(tasks)
