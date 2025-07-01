# utils.py

import os
import secrets
import threading
from PIL import Image
from werkzeug.utils import secure_filename
from flask import url_for, current_app
from flask_mail import Message

# --- Configuration Constants ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
TARGET_IMAGE_SIZE = (200, 200)  # Adjust for higher detail if needed

# --- File Handling Utilities ---

def allowed_file(filename):
    """Check if a file has an allowed image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_picture(form_picture, upload_folder):
    """
    Save an uploaded image after cropping and resizing it to a square.
    Returns the filename or None on failure.
    """
    if not form_picture:
        return None

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(secure_filename(form_picture.filename))
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(upload_folder, picture_fn)

    try:
        img = Image.open(form_picture)

        # Crop to square from center
        width, height = img.size
        crop_size = min(width, height)
        left = (width - crop_size) / 2
        top = (height - crop_size) / 2
        right = (width + crop_size) / 2
        bottom = (height + crop_size) / 2
        img = img.crop((left, top, right, bottom))

        # Resize with high-quality filter
        img = img.resize(TARGET_IMAGE_SIZE, Image.LANCZOS)

        # Save (PNG keeps transparency, if present)
        img.save(picture_path)
        print(f"[INFO] Image saved: {picture_fn}")
        return picture_fn

    except Exception as e:
        print(f"[ERROR] Failed to process image: {e}")
        return None

def delete_picture(old_picture_filename, upload_folder):
    """Delete an image from the upload folder (if it's not the default)."""
    if old_picture_filename and old_picture_filename != 'default_book.png':
        path = os.path.join(upload_folder, old_picture_filename)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"[INFO] Deleted image: {old_picture_filename}")
            except OSError as e:
                print(f"[ERROR] Failed to delete image {old_picture_filename}: {e}")

# --- Email Utilities ---

def _send_async_email(app, msg):
    """Send email using app context in a separate thread."""
    with app.app_context():
        app.extensions['mail'].send(msg)

def send_confirmation_email(user, serializer, mail, app, is_test=False):
    """Send a confirmation email with a timed token."""
    token = user.get_confirmation_token(serializer)
    confirm_url = url_for('confirm_email', token=token, _external=True)

    subject = 'Confirm Your Book Tracker Account'
    body = f"""
Welcome to the Book Tracker!

To confirm your account and start tracking your books, please click on the following link:
{confirm_url}

This link is valid for 30 minutes.

If you did not register for this account, please ignore this email.

Thank you,
The Book Tracker Team
"""

    if is_test:
        subject = f"TEST EMAIL: {subject}"
        body = f"This is a test email. No action required.\n\n{body}"

    msg = Message(subject,
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = body

    threading.Thread(target=_send_async_email, args=(app, msg)).start()
    print(f"[INFO] Email sent to {user.email} (async).")
