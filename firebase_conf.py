import base64
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

# Use /etc/secrets/<filename> on server
# Use ./tourism-hub.json on local

cred = credentials.Certificate('/etc/secrets/<filename>')
firebase_admin.initialize_app(cred)
admin_firestore = firestore.client()
storage_client = storage.Client.from_service_account_json(
    '/etc/secrets/<filename>')
