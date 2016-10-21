import sys
from app import *
from flask import Flask, jsonify, redirect, url_for

app = Flask(__name__)
URL = 'https://meme-tinder.firebaseio.com/'


@app.route('/recommend/<user>', methods=['GET'])
def method(user):
    return jsonify('hey')

@app.route('/_ah/start')
def start():
    system = type('system', (FBSystem, MatFac), {})
    s = system(URL, Encoder(), 0.001)
    s.fetch()


if __name__ == '__main__':
    app.run()
