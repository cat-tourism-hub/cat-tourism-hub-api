
class Establishment:
    def __init__(self, estb_id, b_name, about, b_type, status, banner=None, location=None, contact=None, legals=None):
        self.estb_id = estb_id
        self.b_name = b_name
        self.about = about
        self.b_type = b_type
        self.status = status
        self.banner = banner
        self.location = location
        self.contact = contact
        self.legals = legals


class Location:
    def __init__(self, bldg, street, municipality, barangay):
        self.bldg = bldg
        self.street = street
        self.municipality = municipality
        self.barangay = barangay


class Contact:
    def __init__(self, email, phone, website, social_link):
        self.email = email
        self.phone = phone
        self.website = website
        self.social_link = social_link


class HotelItemDetails:
    def __init__(self, name, price, pax=0, category=None, collection=None, photo_link=[], info=[]):
        self.name = name
        self.price = price
        self.pax = pax
        self.category = category
        self.collection = collection
        self.photo_link = photo_link
        self.info = info


class RestaurantItemDetails:
    def __init__(self, name, price, serving, category,  collection, photo_link=[], info=[]):
        self.name = name
        self.photo_link = photo_link
        self.category = category
        self.price = price
        self.serving = serving
        self.collection = collection
        self.info = info
