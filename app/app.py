from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_babel import Babel, gettext
from flask_pymongo import PyMongo
from passlib.hash import sha256_crypt
# import os

app = Flask(__name__)
# app.secret_key = os.urandom(24)
app.secret_key = 'Secret key string for session cookie hash'

# app.config['MONGO_URI'] = 'mongodb://localhost:27017/db'
app.config['MONGO_URI'] = '<MONGO_URI>'
app.config['BABEL_DEFAULT_LOCALE'] = 'es'

babel = Babel(app)
mongo = PyMongo(app)

# Function to retrieve a file/image from MongoDB using its name
@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)   

# Function that checks if there is a user session stored and if so assign it to g.user
@app.before_request
def before_request():
        g.user = None
        if 'user' in session:
            g.user = session['user']

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Function that saves new session
@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session['user']

    return 'Not logged in!'

# Function that removes current session
@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return redirect(url_for('index')) 

# Function that updates language in session
@app.route('/language/<language>')
def set_language(language=None):
    session['lang'] = language
    return redirect(url_for('index'))

# Function that changes application locale and set corresponding translations
@babel.localeselector
def get_locale():
    try:
        lang = session['lang']
    except KeyError:
        lang = None 
    
    if lang is not None:
        return lang

    return request.accept_languages.best_match(['es', 'eu_ES', 'en'])

from visitor import *
from owner import *

if __name__ == "__main__": 
  app.run()