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

        partners_list = []
        for partner in partners:
            partner_dict = partner.to_dict()
            partner_dict['id'] = partner.id
            partners_list.append(partner_dict)

        return partners_list
    except Exception as e:
        print(e)
        return jsonify({'Error': str(e)}), 500


@views.route('/add-to-order/<itemId>', methods=['POST'])
def add_to_order(item_id):
    pass
