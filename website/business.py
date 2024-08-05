import base64
from flask import Blueprint, request, jsonify
import json
import re
from website.jsonify_decoder import decode_jsonify
from .serializer import serialize_data
from pyrebase_conf import *
from .image_upload import *
from .strings import *
from firebase_conf import admin_firestore as db
from datetime import datetime
from google.api_core.exceptions import DeadlineExceeded
from firebase_admin import auth

business = Blueprint('business', __name__)


def decode_base64(data):
    if data:
        return base64.b64decode(data)
    return None


@business.route('/establishment/<user_uid>', methods=['GET'])
def get_establishment_details(user_uid):
    try:
        partner_ref = db.collection(PARTNERS).document(user_uid)
        partner_doc = partner_ref.get(timeout=10)
        if partner_doc.exists:
            return partner_doc.to_dict()
        else:
            return jsonify('Error: No such partner')
    except DeadlineExceeded:
        return jsonify({"Error": "Network timed out. Please check internet connection."}), 504
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


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
            result = auth.create_user(
                email=email,
                email_verified=False,
                password=password,
            )
            user_uid = result.uid

        except auth.EmailAlreadyExistsError:
            return jsonify({'Error': 'Email already exists.'}), 400
        except Exception as e:
            return jsonify({'Error': str(e)}), 500

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

                upload_res = upload_image_to_firebase(
                    path=abs_path, image=image)
                response_data, status_code = decode_jsonify(upload_res)
                # Check the status code
                if status_code == 201:
                    result.append(abs_path)

        except Exception as e:
            return jsonify({'Error': 'Image upload failed'}), 500

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
            return jsonify({'Error': 'Database insertion failed'}), 500

        try:
            # Create account role for email in firestore
            db.collection('users').document(user_uid).set({
                'role': 'Business Account'
            })
        except Exception as e:
            return jsonify({'Error': 'User info insertion failed', 'details': str(e)}), 500

        return jsonify({'message': 'Data inserted successfully!'}), 201


@business.route('/establishment/update/<uid>', methods=['POST'])
def update_establishment_details(uid):
    data = request.get_json()
    if uid:
        try:
            db.collection(PARTNERS).document(uid).update(data)
            return jsonify({'Success': 'Changes has been saved.'}), 201
        except Exception as e:
            return jsonify({'Error': str(e)}), 500
    return jsonify({'Error': 'Invalid Partner ID'}), 500


@business.route('/update_amenities/<uid>', methods=['POST'])
def update_amenities_facilities(uid):
    token = request.headers.get('Authorization')
    data = request.json

    if not token:
        return jsonify({'error': 'Authorization header missing'}), 401

    # Verify the ID token and get the user's UID
    try:
        decoded_token = auth.verify_id_token(token)
        user_uid = decoded_token['uid']
    except Exception as e:
        return jsonify({'error': 'Token verification failed'}), 401

    # Check if the authenticated user's UID matches the UID in the request
    if user_uid != uid:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        # Initialize facilities_amenities list
        amenities = []
        facilities = {}

        # Process the data and populate facilities_amenities
        for item in data:
            heading = item.get('heading')

            if heading is not None:
                icon_pack = item.get('icon', None).get('pack')
                icon_key = item.get('icon', None).get('key')
                subfields = item.get('subFields', None)

                # Create each facility item
                facility_item = {
                    'heading': heading,
                    'icon': {
                        'pack': icon_pack,
                        'key': icon_key
                    },
                    'subFields': subfields,
                }
                # Add the facility item to facilities_amenities list
                amenities.append(facility_item)

            # Get images from frontend
            images = item.get('images', {})
            photo_data = {}  # Reset photo_data for each item

            if images:
                for img in images:
                    file = decode_base64(img['image'])
                    photo_data.update({img['title']: file})

                for title, image in photo_data.items():
                    abs_path = f'{uid}/facilities/{title}'
                    result = upload_image_to_firebase(
                        path=abs_path, image=image)
                    if result and not isinstance(result, dict):
                        facilities.update({title: abs_path})
                    elif isinstance(result, dict) and 'error' in result:
                        # Return error if upload_image_to_firebase failed
                        return jsonify(result), 400

        # Update or set the facilities_amenities in Firebase
        db.collection(PARTNERS).document(uid).update({
            'amenities': amenities,
            'facilities': facilities
        })

        return jsonify({'message': 'Data stored successfully in Firestore'}), 201
    except Exception as e:
        return jsonify({'Error': 'Please refresh the page and try again.'}), 500


@business.route('/policies/<uid>', methods=['POST'])
def policies(uid):
    if uid:
        policy = request.json
        try:
            db.collection(PARTNERS).document(uid).update({'policies': policy})
            return jsonify({'message': 'Policy is updated'}), 201
        except:
            return jsonify({'Error': 'Policy update fail.'}), 500


@business.route('/services/<uid>', methods=['GET'])
def fetch_products(uid):
    if uid:
        try:
            # Query the services subcollection under the specific partner document
            services_ref = db.collection(
                PARTNERS).document(uid).collection(SERVICES)
            services = services_ref.get()
            service_list = []
            for service in services:
                service_data = service.to_dict()
                service_data['id'] = service.id
                service_list.append(service_data)

            return jsonify(service_list), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Authorization header missing'}), 401


@business.route('<partnerId>/services/edit/<itemId>', methods=['POST'])
def edit_product(partnerId, itemId):
    token = request.headers.get('Authorization')
    data = request.json
    if not partnerId:
        return jsonify({'Error': 'Partner\'s ID is missing'}), 401

    try:
        decoded_token = auth.verify_id_token(token)
        user_uid = decoded_token['uid']
    except Exception as e:
        return jsonify({'Error': 'Token verification failed'}), 401

    # Check if the authenticated user's UID matches the UID in the request
    if partnerId != user_uid:
        return jsonify({'Error': 'Unauthorized'}), 401

    try:
        # Handle file uploads
        photos = data.get('photos', [])

        photo_data = {}
        for photo in photos:
            file = decode_base64(photo['image'])
            photo_data.update({photo['title']: file})

        # Upload images to Firebase and store URLs
        photo_urls = []
        for title, image in photo_data.items():
            abs_path = f'{partnerId}/services/{title}'
            result = upload_image_to_firebase(
                path=abs_path, image=image)
            if result and not isinstance(result, dict):
                photo_urls.append(abs_path)
            elif isinstance(result, dict) and 'error' in result:
                # Return error if upload_image_to_firebase failed
                return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    try:
        # Insert into Firestore under the new subcollection
        db.collection(PARTNERS).document(partnerId).collection(SERVICES).document(itemId).update({
            'name': data['name'],
            'price': data['price'],
            'category': data['category'],
            'desc': data['desc'],
            'pricePer': data['pricePer'],
            'included': data['included'],
            'availabilityStatus': True,
            'updatedOn': datetime.now(),
            'photos': photo_urls,
            'otherServices': data['otherServices']
        })
        return jsonify({'success': 'Product added successfully'}), 201

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@business.route('<partnerId>/services/add', methods=['POST'])
def add_product(partnerId):
    token = request.headers.get('Authorization')
    data = request.json
    print(data['photos'])
    if not partnerId:
        return jsonify({'Error': 'Partner\'s ID is missing'}), 401

    try:
        decoded_token = auth.verify_id_token(token)
        user_uid = decoded_token['uid']
    except Exception as e:
        return jsonify({'Error': 'Token verification failed'}), 401

    # Check if the authenticated user's UID matches the UID in the request
    if partnerId != user_uid:
        return jsonify({'Error': 'Unauthorized'}), 401

    try:
        # Handle file uploads
        photos = data.get('photos', [])

        photo_data = {}
        for photo in photos:
            file = decode_base64(photo['image'])
            photo_data.update({photo['title']: file})
            print(photo_data)

        # Upload images to Firebase and store URLs
        photo_urls = []
        for title, image in photo_data.items():
            abs_path = f'{partnerId}/services/{title}'
            result = upload_image_to_firebase(
                path=abs_path, image=image)
            if result and not isinstance(result, dict):
                photo_urls.append(abs_path)
            elif isinstance(result, dict) and 'error' in result:
                # Return error if upload_image_to_firebase failed
                return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    try:
        # Insert into Firestore under the new subcollection
        db.collection(PARTNERS).document(partnerId).collection(SERVICES).add({
            'partnerId': partnerId,
            'name': data['name'],
            'price': data['price'],
            'category': data['category'],
            'desc': data['desc'],
            'pricePer': data['pricePer'],
            'included': data['included'],
            'availabilityStatus': True,
            'createdOn': datetime.now(),
            'photos': photo_urls,
            'otherServices': data['otherServices']
        })
        return jsonify({'success': 'Product added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@business.route('/migrate-services', methods=['POST'])
def migrate_services():
    try:
        # Get all documents in the 'services' collection
        services_ref = db.collection('services')
        services_docs = services_ref.stream()

        for service_doc in services_docs:
            service_data = service_doc.to_dict()
            partner_id = service_data.get('partnerId')

            if partner_id:
                # Add service to the new subcollection under the partner document
                partner_services_ref = db.collection('partners').document(
                    partner_id).collection('services')
                partner_services_ref.document(service_doc.id).set(service_data)

                # Optionally delete the old document
                services_ref.document(service_doc.id).delete()

        return 'Migration completed successfully!', 200

    except Exception as e:
        return f'An error occurred: {e}', 500

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
