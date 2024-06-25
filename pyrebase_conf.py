import pyrebase

config = {
    'apiKey': 'AIzaSyCsNbjkt1WVCBy2p86w0gSDmMjyckMSr28',
    'authDomain': 'tourism-hub.firebaseapp.com',
    'projectId': 'tourism-hub',
    'storageBucket': 'tourism-hub.appspot.com',
    'messagingSenderId': '70758533530',
    'appId': '1:70758533530:web:be9b0e8b03602015c05223',
    'measurementId': 'G-D4R4Y6DCXW',
    'databaseURL': '',
}

firebase = pyrebase.initialize_app(config)
user_auth = firebase.auth()
bucket = firebase.storage()
