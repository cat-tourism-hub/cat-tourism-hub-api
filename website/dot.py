from flask import Blueprint, session, render_template, redirect, url_for, request, jsonify
from .serializer import *
from pyrebase_conf import *
from firebase_conf import admin_firestore as db
from .models import *
from .auth import authenticate_user
from .db_query import *
from .strings import *
from flask_mail import Message

dot = Blueprint('dot', __name__, static_folder='static',
                template_folder='templates/dot')


@dot.route('/', methods=['POST', 'GET'])
def dot_login():
    if request.method == POST:
        email = request.form['email']
        password = request.form['password']
        error = ''
        try:
            user = user_auth.sign_in_with_email_and_password(email, password)
            if user:
                session['email'] = email
                session['username'] = user.get('displayName', '')
                session['idToken'] = user['idToken']

            return redirect(url_for('dot.dot_admin'))

        except Exception as e:
            error = 'Incorrect email or password.'
        return render_template('dot-login.html', error=error)
    return render_template('dot-login.html')


@dot.route('/admin')
def dot_admin():
    if EMAIL in session:
        return render_template('admin.html')
    return redirect(url_for('dot.dot_login'))


# def get_applicants_count():
#     query = db.collection(ESTABLISHMENT).where('status', '==', 'Pending').get()
#     count = len(query)
#     return count


@dot.route('/active')
def active_est():
    if EMAIL in session:
        return render_template('admin.html')
    return redirect(url_for('dot.dot_login'))


@dot.route('/applicants', methods=['POST', 'GET'])
def applicants():
    applicants = []
    if EMAIL in session:
        data = get_all_business()
        applicants = []
        for establishment in data:
            if establishment['status'] == PENDING:
                applicants.append(Establishment(
                    establishment.get('id'), establishment.get(
                        'name', ''), establishment.get('about', ''), establishment.get('type', ''), establishment.get('status', '')))

        return render_template('applicant.html', applicants=applicants)
    return redirect(url_for('dot.dot_login'))
