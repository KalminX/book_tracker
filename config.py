# config.py

import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
basedir = os.path.abspath(os.path.dirname(__file__))

# Import the db instance from models.py
import sys
sys.path.append(os.path.dirname(__file__))  # ✅ Add current directory to sys.path

from models import db, User

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Application configuration class.
    Loads settings from environment variables.
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Upload Folder Configuration for book covers
    UPLOAD_FOLDER_BASE = 'static' # Base directory for static files
    UPLOAD_FOLDER_SUB = os.path.join('images', 'book_covers') # Subdirectory for book covers

    # Mail Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ("true", "1", "t")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in ("true", "1", "t")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")


def create_app():
    """
    Factory function to create and configure the Flask application.
    Initializes extensions and sets up the user loader.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the upload folder exists
    # app.root_path gives the path to the directory containing the app.py file
    upload_path = os.path.join(app.root_path, Config.UPLOAD_FOLDER_BASE, Config.UPLOAD_FOLDER_SUB)
    os.makedirs(upload_path, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_path # Set the full path in app.config

    # Initialize Extensions with the app
    # Use the 'db' instance imported from models.py
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login" # The view function name for the login page

    mail = Mail(app)

    # Serializer for secure token generation (e.g., for email confirmation)
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    @login_manager.user_loader
    def load_user(user_id):
        """
        Callback to reload the user object from the user ID stored in the session.
        """
        return User.query.get(int(user_id))

    return app, db, login_manager, mail, serializer

