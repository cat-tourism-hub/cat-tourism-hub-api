from flask import Flask, send_from_directory, redirect
from flask_mysqldb import MySQL
from flask_mail import Mail
from .config import Config
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(Config)

    from website.views import views

    from website.business import business
    from website.dot import dot

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(business, url_prefix='/business')
    app.register_blueprint(dot, url_prefix='/dot')

    return app
