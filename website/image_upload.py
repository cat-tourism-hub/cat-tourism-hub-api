from flask import jsonify
from pyrebase_conf import *
from .strings import *


def upload_image_to_firebase(path, image):
    """
    Uploads a single image to Firebase storage and returns the shortened URL.
    """
    try:
        bucket.child(path).put(image)
        return jsonify({'SUCCESS ': f'Image uploaded successfully.'}), 201
    except Exception:
        return jsonify({'ERROR ': f'Error uploading {path}'}), 500
