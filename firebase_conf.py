import base64
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# Use /etc/secrets/<filename> on server
# Use ./tourism-hub.json on local

cred = credentials.Certificate('./tourism-hub.json')
firebase_admin.initialize_app(cred)
admin_firestore = firestore.client()
storage_client = storage.Client.from_service_account_json(
    './tourism-hub.json')
