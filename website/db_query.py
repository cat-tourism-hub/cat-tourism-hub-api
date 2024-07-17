import json
from flask import jsonify, session
from firebase_conf import admin_firestore as db
from pyrebase_conf import *
from website.url_shortener import shorten_url
from .strings import *
from firebase_admin import firestore


def upload_image_to_firebase(path, image, token):
    """
    Uploads a single image to Firebase storage and returns the shortened URL.
    """
    try:
        bucket.child(path).put(image)
        image_link = shorten_url(bucket.child(path).get_url(token))
        return image_link
    except Exception as e:
        return jsonify({f'Error uploading {path}: {e}'})
