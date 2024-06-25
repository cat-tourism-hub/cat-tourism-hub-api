import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage


service_account_info = {
    "type": os.environ.get('tourism-hub-json')['TYPE'],
    "project_id": os.environ.get('tourism-hub-json')['PROJECT_ID'],
    "private_key_id": os.environ.get('tourism-hub-json')['PROJECT_KEY_ID'],
    "private_key": os.environ.get('tourism-hub-json')['PRIVATE_KEY'],
    "client_email": os.environ.get('tourism-hub-json')['CLIENT_EMAIL'],
    "client_id": os.environ.get('tourism-hub-json')['CLIENT_ID'],
    "auth_uri": os.environ.get('tourism-hub-json')['AUTH_URI'],
    "token_uri": os.environ.get('tourism-hub-json')['TOKEN_URI'],
    "auth_provider_x509_cert_url": os.environ.get('tourism-hub-json')['AUTH_PROVIDER_X509_CERT_URL'],
    "client_x509_cert_url": os.environ.get('tourism-hub-json')['CLIENT_X509_CERT_URL'],
    "universe_domain": os.environ.get('tourism-hub-json')['UNIVERSE_DOMAIN'],
}


cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
admin_firestore = firestore.client()
storage_client = storage.Client.from_service_account_json(service_account_info)
