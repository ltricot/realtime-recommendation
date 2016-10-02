from model2 import *
system = type('system', (FBSystem, MatFac), {})
s = system('https://meme-tinder.firebaseio.com/', Encoder(), 0.001)
s.fetch()

while True:
    import time
    time.sleep(1)
