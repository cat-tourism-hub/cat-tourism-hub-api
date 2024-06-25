import json
from flask import jsonify, session
from firebase_conf import admin_firestore as db
from pyrebase_conf import *
from website.url_shortener import shorten_url
from .strings import *
from firebase_admin import firestore


def get_all_business():
    """
    The function `get_all_business` retrieves details of all establishments by performing a JOIN query on
    the `establishment`, `contacts`, and `location` tables in a database.
    :return: A list of dictionaries representing all establishments with their details including name,
    about, type, banner, contact information (email, phone, social links, website), and location
    information (barangay, building, municipality, street). 
    Used in the views.py file
    """
    with current_app.app_context():
        cursor = mysql.connection.cursor()
        try:
            # Perform a JOIN query to get all details
            cursor.execute("""
                SELECT
                    e.estb_id, e.name, e.about, e.type,
                    e.stats, e.banner,
                    c.email, c.phone, c.social_link,
                    c.website,
                    l.brgy, l.bldg,
                    l.municipality, l.street
                FROM
                    establishment e
                JOIN
                    contacts c ON e.contact_id = c.contact_id
                JOIN
                    location l ON e.location_id = l.location_id

            """)
            results = cursor.fetchall()

            if not results:
                return None  # Handle case where no data is found

            # Combine results into a single dictionary
            establishments = []
            for row in results:
                business = {
                    'id': row[0],
                    'name': row[1],
                    'about': row[2],
                    'type': row[3],
                    'status': row[4],
                    'banner': row[5],
                    'contact': {
                        'email': row[6],
                        'phone': row[7],
                        'social_link': row[8],
                        'website': row[9]
                    },
                    'location': {
                        'barangay': row[10],
                        'bldg': row[11],
                        'municipality': row[12],
                        'street': row[13]
                    }
                }
                establishments.append(business)

            return establishments
        except Exception as e:
            print(e)
            return None
        finally:
            cursor.close()


def upload_image_to_firebase(path, image, token):
    """
    Uploads a single image to Firebase storage and returns the shortened URL.
    """
    try:
        bucket.child(path).put(image)
        image_link = shorten_url(bucket.child(path).get_url(token))
        return image_link
    except Exception as e:
        return jsonify({f'error: Error uploading {path}: {e}'})


# def save_to_db(user_uid, location, contact, establishment, logo_link, banner_link, buss_link, sanit_link, dot_link):
#     # The above Python code snippet is saving establishment details to a MySQL database. It performs
#     # the following steps:
#     # Save establishment details to MySQL database
#     with current_app.app_context():
#         cursor = mysql.connection.cursor()
#         try:
#             # Insert contact data into the 'contact' table
#             cursor.execute("""
#                 INSERT INTO contacts (name, email, phone, social_link, website)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (contact['name'], contact['email'], contact['phone'], contact['social_link'], contact['website']))
#             contact_id = cursor.lastrowid

#             # Insert location data into the 'location' table
#             cursor.execute("""
#                 INSERT INTO location (brgy, bldg, municipality, street)
#                 VALUES (%s, %s, %s, %s)
#             """, (location['brgy'], location['bldg'], location['municipality'], location['street']))
#             location_id = cursor.lastrowid

#             # Insert legals data into the 'legals' table
#             cursor.execute("""
#                 INSERT INTO legals (buss_perm, sanit_perm, dot_cert)
#                 VALUES (%s, %s, %s)
#             """, (buss_link, sanit_link, dot_link))
#             legals_id = cursor.lastrowid

#             # Insert establishment data into the 'establishment' table
#             cursor.execute("""
#                 INSERT INTO establishment (name, about, type, stats, logo, banner, contact_id, location_id, legals_id, user_uid)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """, (establishment['name'], establishment['about'],  establishment['type'],  establishment['status'], logo_link, banner_link, contact_id, location_id, legals_id, user_uid))

#             mysql.connection.commit()
#             return jsonify({'message': 'Data inserted successfully!'}), 201
#         except Exception as e:
#             print(e)
#             mysql.connection.rollback()
#             return jsonify({'error': str(e)}), 500
#         finally:
#             cursor.close()


# def get_location_details(reference):
#     location_document = reference.get().to_dict()

#     bldg = location_document.get('bldg')
#     street = location_document.get('street')
#     municipality = location_document.get('municipality')
#     barangay = location_document.get('barangay')

#     return f"{bldg}, {street}, {barangay}, {municipality}"


# def get_contact_details(reference):
#     contact_document = reference.get().to_dict()

#     # Access data from contact document
#     email = contact_document.get('email')
#     phone = contact_document.get('phone')
#     website = contact_document.get('website')
#     social_link = contact_document.get('social_link')

#     return f"{email}, {phone}, {website}, {social_link}"


def is_firestore_success(response):
    if 'update_time' in str(response):
        return True
    return False


####################################
#  CRUD FOR ITEM IN CATEGORY       #
####################################
# def create_item_in_category(category, header, photo, name, price):
#     user_uid = session['user_uid']
#     photo_links = []

#     with current_app.app_context():
#         cursor = mysql.connection.cursor()
#         try:
#             # Upload each photo and store the links in a list
#             if photo:
#                 file_path = f'{user_uid}/products/{category}/{name}/{photo.filename}'
#                 bucket.child(file_path).put(photo)
#                 photo_links.append(bucket.child(
#                     file_path).get_url(session['idToken']))

#             # Convert photo_links list to JSON string
#             photo_links_json = json.dumps(photo_links)

#             # Insert product data into products table
#             cursor.execute("""
#                 INSERT INTO products (name, category, price, photo_links, estb_id)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (name, header, price, photo_links_json, session['b_info']['estb_id']))

#             mysql.connection.commit()
#         except Exception as e:
#             print(e)
#             mysql.connection.rollback()
#         finally:
#             cursor.close()


def upload_item_photo(category, name, photo):
    user_uid = session['user_uid']
    file_path = f'{user_uid}/products/{category}/{name}/{photo.filename}'
    doc_ref = db.collection(PRODUCTS).document(f'{user_uid}')

    data = doc_ref.get().to_dict()
    name = replace_underscore_to_space(name)

    if 'photo_link' not in data[name]:
        data[name]['photo_link'] = []
    try:
        data[name]['photo_link'].extend([file_path])
        bucket.child(file_path).put(photo, session['idToken'])
        result = doc_ref.update(data)
        if is_firestore_success(result):
            return file_path
    except Exception as e:
        print(e)


def update_item_details(collection, name, price, pax, newInfo):
    user_uid = session['user_uid']
    try:
        doc_ref = db.collection(
            PRODUCTS).document(f'{user_uid}')

        document = doc_ref.get()

        if document.exists:
            document_data = document.to_dict()
            name = replace_underscore_to_space(name)
            if 'info' not in document_data[name]:
                document_data[name]['info'] = []

            document_data[name]['info'] = newInfo
            document_data[name]['price'] = price

            if collection == AMENITIES:
                document_data[name]['pax'] = pax
            elif collection == RESTAURANT:
                document_data[name]['serving'] = pax

            result = doc_ref.update(document_data)
            if is_firestore_success(result):
                return SUCCESS
    except Exception as e:
        print(e)


def remove_item_image(path, name):
    token = session.get('idToken')
    user_uid = session['user_uid']
    try:
        bucket.delete(path, token)
        doc_ref = db.collection(
            PRODUCTS).document(f'{user_uid}')

        document = doc_ref.get()

        if document.exists:
            document_data = document.to_dict()
            name = replace_underscore_to_space(name)
            if document_data and document_data.get(name) and document_data[name].get('photo_link'):
                document_data[name]['photo_link'].remove(path)
                result = doc_ref.update(document_data)
                if is_firestore_success(result):
                    return SUCCESS
    except Exception as e:
        return e


def remove_item(name):
    user_uid = session['user_uid']
    name = replace_underscore_to_space(name)
    try:
        doc_ref = db.collection(PRODUCTS).document(f'{user_uid}')
        data = doc_ref.get().to_dict()
        if name in data:
            photo_links = data[name]['photo_link']
            for link in photo_links:
                bucket.delete(link, session['idToken'])

            # Updates the products list of establishment
            result = doc_ref.update({
                name: firestore.DELETE_FIELD
            })
            if is_firestore_success(result):
                return SUCCESS

    except Exception as e:
        print(e)


#################################
#  ADD / GET AMENITIES          #
#################################
def get_products():
    estb_type = session['b_info']['b_type']
    estb_name = session['b_info']['b_name']
    products = []
    try:
        # Execute the query to fetch products in firestore
        estb_ref = db.collection(estb_type).document(
            estb_name).collection(PRODUCTS)

        for product in estb_ref.stream():
            products.append(product)

        return products

    except Exception as e:
        print(f'E: {e}')
        return None


def create_products_db(details):
    location = f"{details['location']['bldg']}, {details['location']['street']}, {details['location']['brgy']}, {details['location']['municipality']}"
    try:
        estb_ref = db.collection(details['establishment']['type']).document(
            details['establishment']['name'])
        estb_ref.set({'location': location})

        estb_ref.collection(PRODUCTS).doc('default').set({})
    except Exception as e:
        return e
