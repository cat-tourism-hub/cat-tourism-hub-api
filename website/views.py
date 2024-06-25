import os
from flask import Blueprint, redirect, jsonify
from website.db_query import get_all_business
from .strings import *

views = Blueprint('views', __name__,
                  static_folder='website/frontend/build', template_folder='templates')


@views.route('/')
def index():
    docs = get_all_business()
    if docs:
        return docs
    return


@views.route('/accommodation')
def accommodation():
    return redirect('/')


@views.route('/restaurant')
def restaurant():
    return redirect('/')


@views.route('/car-rental')
def car_rental():
    return redirect('/')
