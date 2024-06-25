import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage

service_account_info = json.loads(os.getenv('FIREBASE_SERVICE_ACCT'))

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
admin_firestore = firestore.client()
storage_client = storage.Client.from_service_account_json(service_account_info)
