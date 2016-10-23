import workers
import app
from threading import Thread
from gapis import tqclient


URL = 'https://meme-tinder.firebaseio.com/'

#--code...
q = tqclient.Queue('http://127.0.0.1:5000/')
worker = workers.Worker(app.MatFac(0.001), q, URL, app.Encoder())
worker.run()
