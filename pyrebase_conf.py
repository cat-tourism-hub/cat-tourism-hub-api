import json
import os
import pyrebase

config = {
    'apiKey': os.environ.get('APIKEY'),
    'authDomain': os.environ.get('AUTHDOMAIN'),
    'projectId': os.environ.get('PROJECTID'),
    'storageBucket': os.environ.get('STORAGEBUCKET'),
    'messagingSenderId': os.environ.get('MESSAGINGSENDERID'),
    'appId': os.environ.get('APPID'),
    'measurementId': os.environ.get('MEASUREMENTID'),
    'databaseURL': '',
}

firebase = pyrebase.initialize_app(config)
user_auth = firebase.auth()
bucket = firebase.storage()
