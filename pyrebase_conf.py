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

# config = {
#     'apiKey': 'AIzaSyCsNbjkt1WVCBy2p86w0gSDmMjyckMSr28',
#     'authDomain': 'tourism-hub.firebaseapp.com',
#     'projectId': 'tourism-hub',
#     'storageBucket': 'tourism-hub.appspot.com',
#     'messagingSenderId': '70758533530',
#     'appId': '1:70758533530:web:be9b0e8b03602015c05223',
#     'measurementId': 'G-D4R4Y6DCXW',
#     'databaseURL': '',
# }
firebase = pyrebase.initialize_app(config)
user_auth = firebase.auth()
bucket = firebase.storage()
