import os
from flask import Blueprint, redirect, jsonify
from firebase_conf import admin_firestore as db
from .strings import *
from google.cloud.firestore_v1.base_query import FieldFilter

views = Blueprint('views', __name__)


@views.route('/')
def index():
    try:
        partners_ref = db.collection(
            PARTNERS).where(filter=FieldFilter("estb.status", "==", "Pending"))
        partners = partners_ref.get()
        partners_list = [partner.to_dict() for partner in partners]

        return partners_list

    except Exception as e:
        return jsonify({'error': str(e)}), 500
