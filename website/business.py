import base64
from flask import Blueprint, session, render_template, redirect, url_for, request, jsonify, flash
from .serializer import serialize_data
from pyrebase_conf import *
from .auth import *
from .db_query import *
from .strings import *
from firebase_conf import admin_firestore as db
from google.cloud.firestore_v1.base_query import FieldFilter

business = Blueprint('business', __name__)


@business.route('/')
def business_index():
    if EMAIL in session:
        return redirect(url_for('business.dashboard'))
    return redirect(url_for('business.login'))


@business.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('email', None)
    session.pop('username', None)
    if request.method == POST:
        # login the user
        result = authenticate_user(request)

        if result == SUCCESS:
            # extract business details
            business_details = get_establishment_details(
                session.get('user_uid'))
            if business_details:

                session['b_info'] = {
                    'estb_id': business_details['establishment'].get('estb_id', ''),
                    'b_name': business_details['establishment'].get('name', ''),
                    'b_type': business_details['establishment'].get('type', ''),
                    'status': business_details['establishment'].get('stats', ''),
                    'contact': business_details.get('contact', {}),
                    'location': business_details.get('location', {}),
                    'legals': business_details.get('legals', {})
                }
                session['logo'] = bucket.child(
                    session.get('user_uid')+'/logo.png').get_url(session['idToken'])

            return redirect(url_for('business.dashboard'))
        elif result == INVALID_CREDENTIALS:
            return render_template('b-login.html', error='Invalid email or password.')
        else:
            return render_template('b-login.html', error=result)
    if EMAIL in session:
        return redirect(url_for('business.dashboard'))

    return render_template('b-login.html')


def decode_base64(data):
    if data:
        return base64.b64decode(data)
    return None


@business.route('/establishment/<user_uid>')
def get_establishment_details(user_uid):
    try:
        partner_ref = db.collection("partners").document(user_uid)
        partner_doc = partner_ref.get()
        if partner_doc.exists:
            return partner_doc.to_dict()
        else:
            return jsonify('Error: No such partner')
    except Exception as e:
        print(e)
        return None


@business.route('/register', methods=['POST'])
def register():
    if request.method == POST:
        data = request.get_json()
        try:
            location, contact, establishment = serialize_data(data)
        except Exception as e:
            return jsonify({'error': 'Data serialization failed', 'details': str(e)}), 400

        try:
            # Extract additional form data
            email = data.get('contact', {}).get('email', '')
            contact_name = data.get('contact', {}).get('name', '')
            business_name = data.get('name', '')
            password = f'{contact_name}@{business_name}'

            # Create business account

            result = user_auth.create_user_with_email_and_password(
                email=email, password=password)

            user_uid = result['localId']
            token = result['token']
        except Exception as e:
            return jsonify({'error': 'Account creation failed', 'details': str(e)}), 500

        try:
            # Parse files
            logo = decode_base64(data['logo'])
            banner = decode_base64(data['banner'])
            buss_perm = decode_base64(data['bussPerm'])
            sanit_perm = decode_base64(data['sanitPerm'])
            dot_cert = decode_base64(data['dotCert'])

            # Save images to Firebase storage
            images = {
                'logo': logo,
                'banner': banner,
                'buss_perm': buss_perm,
                'sanit_perm': sanit_perm,
                'dot_cert': dot_cert
            }

            result = []
            for image_name, image in images.items():
                abs_path = f'{user_uid}/{image_name}.png'
                image_link = upload_image_to_firebase(
                    path=abs_path, image=image, token=token)
                if image_link:
                    result.append(image_link)

        except Exception as e:
            return jsonify({'error': 'Image upload failed', 'details': str(e)}), 500

        try:
            # Insert partners details to firestore
            db.collection(PARTNERS).document(user_uid).set({
                'estb': establishment, 'location': location, 'contact': contact,
                'logo': result[0],
                'banner': result[1],
                'legals': {
                    'bussPermit': result[2],
                    'sanitPerm': result[3],
                    'dotCert': result[4]
                }
            })

        except Exception as e:
            return jsonify({'error': 'Database insertion failed', 'details': str(e)}), 500

        try:
            # Create account role for email in firestore
            db.collection('users').document(user_uid).set({
                'role': 'Business Account'
            })
        except Exception as e:
            return jsonify({'error': 'Database insertion failed', 'details': str(e)}), 500

        return jsonify({'message': 'Data inserted successfully!'}), 201


@business.route('/services/<uid>', methods=['GET'])
def rooms(uid):
    if uid:
        try:
            services_ref = db.collection(
                SERVICES).where(filter=FieldFilter("partnerId", "==", uid))
            services = services_ref.stream()
            service_list = [service.to_dict() for service in services]
            return service_list

            # rooms_ref = db.collection(SERVICES).document(
            #     token).collection(PRODUCTS)
            # rooms = []
            # docs = rooms_ref.get()
            # for doc in docs:

            #     room_data = doc.to_dict()
            #     room_data['id'] = doc.id
            #     rooms.append(room_data)

        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'error': 'Authorization header missing'}), 401


@business.route('/services/<b_name>/add', methods=['POST'])
def add_room(b_name):
    token = request.headers.get('Authorization')
    b_type = request.headers.get('type')
    user_uid = request.headers.get('uid')
    data = request.json
    if token:
        try:
            # Handle file uploads
            photos = data.get('photos', [])
            photo_urls = []
            photo_data = {}
            for photo in photos:
                file = decode_base64(photo['webImage'])
                photo_data.update({photo['title']: file})

             # Upload images to Firebase and store URLs
            for title, image in photo_data.items():
                abs_path = f'{user_uid}/products/rooms/{title}'
                result = upload_image_to_firebase(
                    path=abs_path, image=image, token=token)
                if result and not isinstance(result, dict):
                    photo_urls.append(result)
                elif isinstance(result, dict) and 'error' in result:
                    return result  # Return error if upload_image_to_firebase failed
        except Exception as e:
            return jsonify({'error': str(e)})

        try:
            # Insert into Firebase
            db.collection(SERVICES).add({
                'name': data['name'],
                'price': data['price'],
                'desc': data['desc'],
                'pricePer': data['pricePer'],
                'amenities': data['amenities'],
                'photos': photo_urls
            })
            return jsonify({'success': 'Room added successfully'}), 201

        except Exception as e:
            return jsonify({'error': str(e)})


# @business.route('/restaurant')
# def restaurant():
#     return restaurant_category.get_categories()


# @business.route('/contact')
# def contact():
#     return contact_category.get_page()


# @business.route('/location')
# def location():
#     return location_category.get_page()


# @business.route('/legal-documents')
# def legals():
#     return legals_category.get_page()


# @business.route('/add_item', methods=['POST'])
# def add_item():
#     """
#     The function `add_item` takes input from a form, including a category name, photo, item name, and
#     price, and adds the item to a database, returning a success or error message.
#     :return: a JSON response. If the result of adding the item to the database is successful, it will
#     return a JSON object with the keys 'result' and 'message', where 'result' is set to the value of the
#     variable SUCCESS and 'message' is a string indicating that the item was successfully added. If the
#     result is not successful, it will return a JSON object with the
#     """
#     category_name = request.form.get('category')
#     header = request.form.get('header')
#     item_photo = request.files.get('photo')
#     item_name = request.form.get('name')
#     item_price = request.form.get('price')
#     if item_photo:
#         item_photo.stream.seek(0)
#     result = create_item_in_category(
#         category_name, header, item_photo, item_name, item_price)
#     if result == SUCCESS:
#         return jsonify({'result': SUCCESS, 'message': item_name + ' is successfully added.'})
#     return jsonify({'result': ERROR, 'message': item_name + ' failed to be added.'})


# @business.route('/<header>/<name>', methods=['GET', 'POST'])
# def item_details(header, name):
#     if header == AMENITIES.lower():
#         return amenities_category.item_details(name)
#     return restaurant_category.item_details(name)


# @business.route('/save_changes', methods=['POST'])
# def save_changes_in_product():
#     name = request.form.get('name')
#     collection = request.form.get('collection')
#     price = request.form.get('price')
#     infos = request.form.get('newInfo')
#     newInfo = []

#     if infos:
#         newInfo.extend(info.strip() for info in infos.split(','))

#     if collection == AMENITIES:
#         pax = request.form.get('pax')
#         result = update_item_details(collection,  name, price, pax, newInfo)
#     elif collection == RESTAURANT:
#         serving = request.form.get('serving')
#         result = update_item_details(collection, name, price, serving, newInfo)

#     if result == SUCCESS:
#         return jsonify({'result': SUCCESS, 'message': 'Changes successfully saved.'})
#     return jsonify({'result': ERROR, 'message': 'Changes failed to be saved. Try again later.'}), 500


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @business.route('/add_item_photo', methods=['POST'])
# def add_item_photo():
#     try:
#         file = request.files.get('file')
#         category = request.form.get('category')
#         name = request.form.get('name')

#         if file.filename == '':
#             return jsonify({'error': 'No selected file'})

#         if file and allowed_file(file.filename):
#             file_path = upload_item_photo(
#                 category, name, file)
#             return jsonify({'file_path': file_path})

#         return jsonify({'Error': 'Invalid file format'}), 400
#     except Exception as e:
#         return jsonify({'Error': str(e)})


# @business.route('/delete_item_photo', methods=['DELETE'])
# def delete_item_photo():
#     try:
#         file = request.form.get('file')
#         name = request.form.get('name')
#         remove_item_image(file, name)
#         return jsonify({'message': 'Photo deleted successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @business.route('/delete_item', methods=['DELETE'])
# def delete_item():
#     try:
#         category = request.form.get('category')
#         name = request.form.get('name')

#         remove_item(category, name)
#         return jsonify({SUCCESS: 'Item deleted successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
