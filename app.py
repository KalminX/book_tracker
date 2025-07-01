# app.py

# --- Imports ---
import os
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import SignatureExpired, BadSignature
from flask_migrate import Migrate
from flask_mail import Message
from werkzeug.security import generate_password_hash

# --- Local Module Imports ---
from config import create_app
from utils import allowed_file, save_picture, delete_picture, send_confirmation_email
from models import db, User, Book

# --- App Setup ---
app, db, login_manager, mail, serializer = create_app()
migrate = Migrate(app, db)


# --- Shell Context Processor ---
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Book=Book)


# =======================
#         ROUTES
# =======================

# Home / Book List
@app.route("/")
@login_required
def index():
    base_query = Book.query.filter_by(user_id=current_user.id)
    filter_status = request.args.get('status')
    active_filter = filter_status if filter_status in ['read', 'unread', 'reading', 'finished', 'on-hold'] else 'all'

    if active_filter != 'all':
        books = base_query.filter_by(status=active_filter).all()
    else:
        books = base_query.all()

    total_books = base_query.count()
    read_books_count = base_query.filter_by(status='read').count()
    reading_books_count = base_query.filter_by(status='reading').count()
    finished_books_count = base_query.filter_by(status='finished').count()
    on_hold_books_count = base_query.filter_by(status='on-hold').count()
    unread_books_count = total_books - read_books_count - reading_books_count - finished_books_count - on_hold_books_count
    read_percentage = round((read_books_count / total_books) * 100, 2) if total_books > 0 else 0

    return render_template(
        "index.html",
        books=books,
        total_books=total_books,
        read_books_count=read_books_count,
        reading_books_count=reading_books_count,
        finished_books_count=finished_books_count,
        on_hold_books_count=on_hold_books_count,
        unread_books_count=unread_books_count,
        read_percentage=read_percentage,
        active_filter=active_filter
    )


# Add Book
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        status = request.form.get("status")
        image_file_url = None  # Store GitHub raw URL here

        if 'image' in request.files:
            image = request.files['image']
            if image.filename and allowed_file(image.filename):
                image_file_url = save_picture(image, app.config['UPLOAD_FOLDER'])
                if not image_file_url:
                    flash('Failed to upload image to GitHub.', 'danger')
                    return render_template('add.html', title=title, author=author, genre=genre, status=status)
            elif image.filename != '':
                flash('Invalid image file type.', 'danger')
                return render_template('add.html', title=title, author=author, genre=genre, status=status)

        if not image_file_url:
            image_file_url = url_for('static', filename='default_book.png')

        book = Book(
            title=title,
            author=author,
            genre=genre,
            status=status,
            user_id=current_user.id,
            image_file=image_file_url
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')


# Edit Book
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    book = Book.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        book.title = request.form.get("title")
        book.author = request.form.get("author")
        book.genre = request.form.get("genre")
        book.status = request.form.get("status")

        if 'image' in request.files:
            image = request.files['image']
            if image.filename and allowed_file(image.filename):
                if book.image_file and book.image_file != os.path.join(app.config.get('UPLOAD_FOLDER_SUB', ''), 'default_book.png'):
                    delete_picture(book.image_file, app.config['UPLOAD_FOLDER'])
                
                image_file_url = save_picture(image, app.config['UPLOAD_FOLDER'])
                if not image_file_url:
                    flash('Failed to save image.', 'danger')
                    return render_template('edit.html', book=book)
                
                book.image_file = image_file_url
            elif image.filename != '':
                flash('Invalid image file type.', 'danger')
                return render_template('edit.html', book=book)
        else:
            # Fix old default image path if needed
            if book.image_file == 'default_book.png':
                book.image_file = os.path.join(app.config.get('UPLOAD_FOLDER_SUB', ''), 'default_book.png')

        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', book=book)


# Delete Book
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    book = Book.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if book.image_file != url_for('static', filename='default_book.png'):
        delete_picture(book.image_file, app.config['UPLOAD_FOLDER'])
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted!", "info")
    return redirect(url_for("index"))


# --- Authentication Routes ---

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Attempting login for email: {username}")  # DEBUG PRINT
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}, Confirmed: {user.confirmed}")  # DEBUG PRINT
            if user.check_password(password):
                print("Password check passed!")  # DEBUG PRINT
                if user.confirmed:
                    login_user(user)
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("index"))
                else:
                    flash("Please confirm your email address first.", "warning")
            else:
                print("Password check failed.")  # DEBUG PRINT
                flash("Invalid email or password.", "danger")
        else:
            print("User not found for this email.")  # DEBUG PRINT
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'warning')
            return render_template('register.html', username=username, email=email)
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return render_template('register.html', username=username, email=email)

        new_user = User(email=email, username=username, confirmed=False)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        send_confirmation_email(user=new_user, serializer=serializer, mail=mail, app=app)
        flash("A confirmation email has been sent.", "info")
        return redirect(url_for("login"))

    return render_template("register.html")


# Confirm Email
@app.route("/confirm/<token>")
def confirm_email(token):
    if current_user.is_authenticated:
        flash('Already logged in.', 'info')
        return redirect(url_for('index'))

    try:
        user_id = serializer.loads(token, max_age=3600)['user_id']
        user = User.query.get(user_id)
        if not user:
            flash("Invalid token or user.", "danger")
            return redirect(url_for("login"))
    except SignatureExpired:
        flash("Token expired.", "danger")
        return redirect(url_for("register"))
    except BadSignature:
        flash("Invalid token.", "danger")
        return redirect(url_for("login"))
    except Exception as e:
        flash(f"Confirmation error: {e}", "danger")
        return redirect(url_for("login"))

    if user.confirmed:
        flash("Already confirmed.", "info")
    else:
        user.confirmed = True
        db.session.commit()
        flash("Account confirmed!", "success")

    return redirect(url_for("login"))


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


# Test Email Route (for testing email config)
@app.route("/test-email")
def test_email():
    test_user_email = os.getenv("MAIL_USERNAME")
    if not test_user_email:
        flash("MAIL_USERNAME not set.", "danger")
        return redirect(url_for('index'))

    class TempUser:
        def __init__(self, email):
            self.email = email
            self.id = 0

    temp_user = TempUser(test_user_email)
    send_confirmation_email(user=temp_user, serializer=serializer, mail=mail, app=app, is_test=True)
    flash(f"Test email sent to {test_user_email}.", "success")
    return redirect(url_for('index'))


# --- Password Reset Routes ---

# Forgot Password
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps({'user_id': user.id})
            reset_url = url_for('reset_password', token=token, _external=True)

            subject = "Password Reset Request"
            body = f"""
            To reset your password, click the following link:
            {reset_url}

            If you did not request this, please ignore this email.
            This link expires in 1 hour.
            """

            msg = Message(subject=subject, recipients=[email], body=body)
            mail.send(msg)

            flash("Password reset email sent! Check your inbox.", "info")
        else:
            flash("No account found with that email address.", "warning")

    return render_template('forgot_password.html')


# Reset Password
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    try:
        data = serializer.loads(token, max_age=3600)  # 1 hour expiry
        user_id = data['user_id']
    except SignatureExpired:
        flash("The reset link has expired.", "danger")
        return redirect(url_for('forgot_password'))
    except BadSignature:
        flash("Invalid reset token.", "danger")
        return redirect(url_for('forgot_password'))

    user = User.query.get(user_id)
    if not user:
        flash("Invalid user.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if not password or not password_confirm:
            flash("Please fill out both password fields.", "warning")
            return render_template('reset_password.html', token=token)

        if password != password_confirm:
            flash("Passwords do not match.", "warning")
            return render_template('reset_password.html', token=token)

        user.set_password(password)
        db.session.commit()

        flash("Your password has been reset! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


# --- Main Execution ---
if __name__ == "__main__":
    with app.app_context():
        print(f"DEBUG: DATABASE URI -> {os.getenv('DATABASE_URI')}")
        db.create_all()
        print("Database tables created/checked.")
    app.run(debug=True)
