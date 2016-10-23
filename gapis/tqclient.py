# built-in imports
from urllib.parse import urlencode
import time, json

# internal imports
from .tqserver import Task

# external imports
import requests


class Queue:

    def __init__(self, url):
        self.url = url

    def lease_tasks_by_tag(self, **kwargs):
        tasks = []
        while not tasks:
            r = requests.get(self.url, params=kwargs)
            tasks = [Task(**t) for t in r.json()['tasks']]
            time.sleep(1)
        return tasks

    def add(self, tasks):
        for task in tasks:
            requests.post(self.url, json=task._asdict())

    def delete_tasks(self, tasks):
        requests.delete(self.url, json={'tasks': [t._asdict() for t in tasks]})
