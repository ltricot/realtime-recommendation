"""
    Drop-in replacement for some features of google.appengine.api.taskqueue
module. Testing purposes only. This works in python 3 (the whole point of this
module).

"""

from flask import Flask, jsonify, request
import requests

from collections import namedtuple, defaultdict
import time, json

from testutils import debug

Task = namedtuple('Task', ['tag', 'payload', 'method'])

@debug
class BackEndQueue:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self):
        self.tasks = defaultdict(list)
        self.times = dict()

    def add(self, task):
        self.tasks[task.tag].append(task)
        self.times[task.tag] = time.time()

    def lease_tasks_by_tag(self, lease_seconds, max_tasks, deadline):
        items = list(self.times.items())
        if not items:
            return []
        _, tag = min((t, tag) for tag, t in items)
        return self.tasks[tag][:max_tasks].copy()

    def delete_tasks(self, tasks):
        for task in tasks:
            try:
                self.tasks[task.tag].remove(task)
                self.times[task.tag] = time.time()
            except ValueError:
                pass # already removed?


app = Flask(__name__)
q = BackEndQueue()

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def interact():
    # must organize this better...
    # TO-DO preprocess request data to assert right structure
    if request.method == 'POST': # add task
        q.add(Task(**request.json))
        return jsonify(request.args)

    elif request.method == 'GET': # lease tasks
        # this puts params in lists, so:
        # assert all(len(x) == 1 for x in request.args.values())
        kwargs = {k: int(v[0]) for k, v in dict(**request.args).items()}
        tasks = q.lease_tasks_by_tag(**kwargs)
        tasks = [t._asdict() for t in tasks]
        return jsonify({'tasks': tasks})

    elif request.method == 'DELETE':
        q.delete_tasks(Task(**j) for j in request.json['tasks'])

    return 'not supported' # no idea what that req is


if __name__ == '__main__':
    app.run()
