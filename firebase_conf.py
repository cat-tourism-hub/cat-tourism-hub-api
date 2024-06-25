import base64
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

service_account_base64 = os.environ.get('FIREBASE_SERVICE_ACCT')

service_account_info = json.loads(
    base64.b64decode(service_account_base64).decode('utf-8'))

# service_account_info = {
#     "type": 'service_account',
#     "project_id": os.environ.get('PROJECT_ID'),
#     "private_key_id": os.environ.get('PROJECT_KEY_ID'),
#     "private_key": private_key,
#     "client_email": os.environ.get('CLIENT_EMAIL'),
#     "client_id": os.environ.get('CLIENT_ID'),
#     "auth_uri": os.environ.get('AUTH_URI'),
#     "token_uri": os.environ.get('TOKEN_URI'),
#     "auth_provider_x509_cert_url": os.environ.get('AUTH_PROVIDER_X509_CERT_URL'),
#     "client_x509_cert_url": os.environ.get('CLIENT_X509_CERT_URL'),
#     "universe_domain": os.environ.get('UNIVERSE_DOMAIN'),
# }


cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
admin_firestore = firestore.client()
storage_client = storage.Client.from_service_account_json(service_account_info)
