import json
import os
import pyrebase

config = {
    'apiKey': os.environ.get('PYREBASE_CONF')['APIKEY'],
    'authDomain': os.environ.get('PYREBASE_CONF')['AUTHDOMAIN'],
    'projectId': os.environ.get('PYREBASE_CONF')['PROJECTID'],
    'storageBucket': os.environ.get('PYREBASE_CONF')['STORAGEBUCKET'],
    'messagingSenderId': os.environ.get('PYREBASE_CONF')['MESSAGINGSENDERID'],
    'appId': os.environ.get('PYREBASE_CONF')['APPID'],
    'measurementId': os.environ.get('PYREBASE_CONF')['MEASUREMENTID'],
    'databaseURL': '',
}

firebase = pyrebase.initialize_app(config)
user_auth = firebase.auth()
bucket = firebase.storage()
