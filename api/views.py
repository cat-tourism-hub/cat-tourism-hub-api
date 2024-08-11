import os
from flask import Blueprint, redirect, jsonify
from firebase_conf import admin_firestore as db
from .strings import *
from google.cloud.firestore_v1.base_query import FieldFilter
from google.api_core.exceptions import DeadlineExceeded

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def index():
    try:
        partners_ref = db.collection(
            PARTNERS).where(filter=FieldFilter("estb.status", "==", "Pending"))
        partners = partners_ref.get()
        partners_list = [partner.to_dict() for partner in partners]
        return partners_list
    except Exception as e:
        print(e)
        return jsonify({'Error': str(e)}), 500


@views.route('/add_to_order', methods=['POST'])
def add_to_order():
    pass
