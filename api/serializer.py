from .strings import PENDING


def serialize_loc(bldg, street, municipality, barangay):
    return {
        'bldg': bldg,
        'street': street,
        'municipality': municipality,
        'brgy': barangay
    }


def serialize_contact(name, email, phone, website, social_link):
    return {
        'contact_name': name,
        'email': email,
        'phone': phone,
        'website': website,
        'social_link': social_link
    }


def serialize_est(b_name, about, b_type, status):
    return {
        'name': b_name,
        'about': about,
        'type': b_type,
        'status': status

    }


def serialize_data(request):
    b_type = request.get('type', '')
    b_name = request.get('name', '')
    b_about = request.get('about', '')
    bldg = request.get('location', {}).get('bldg', '')
    street = request.get('location', {}).get('street', '')
    municipality = request.get('location', {}).get('municipality', '')
    barangay = request.get('location', {}).get('barangay', '')
    name = request.get('contact', {}).get('name', '')
    email = request.get('contact', {}).get('email', '')
    tel = request.get('contact', {}).get('phone', '')
    website = request.get('contact', {}).get('website', '')
    socmed = request.get('contact', {}).get('socmed', '')

    location = serialize_loc(bldg, street, municipality, barangay)
    contact = serialize_contact(name, email, tel, website, socmed)
    establishment = serialize_est(b_name, b_about, b_type, PENDING)

    return location, contact, establishment
