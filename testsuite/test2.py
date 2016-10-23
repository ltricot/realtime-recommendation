import app
from gapis import tqclient
from threading import Thread
import sys

URL = 'https://meme-tinder.firebaseio.com/'

#--code...
encoder = app.Encoder()
q = tqclient.Queue('http://127.0.0.1:5000/')
system = app.QueuedFBSystem(q, URL)
system.fetch()
