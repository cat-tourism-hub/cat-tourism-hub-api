# config for mysql database
import os


class Config:
    SECRET_KEY = os.urandom(12)
    MYSQL_HOST = '127.0.0.1'
    MYSQL_USER = 'tourism-hub'
    MYSQL_PASSWORD = 'toor'
    MYSQL_DB = 'tourism-hub'

    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'catanduanestourismhub@gmail.com'
    MAIL_PASSWORD = 'tourismhub@catanduanes2024'
    MAIL_DEFAULT_SENDER = 'catanduanestourismhub@gmail.com'
