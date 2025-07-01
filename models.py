# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import random
from faker import Faker

# Initialize SQLAlchemy outside of app to avoid circular imports
db = SQLAlchemy()

# --- Models ---

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', confirmed={self.confirmed})"

    def set_password(self, password):
        """Hashes the given password and stores it in password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the given password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def get_confirmation_token(self, serializer, expires_sec=1800):
        """Generate a signed, time-limited token for email confirmation."""
        return serializer.dumps({'user_id': self.id})

    @staticmethod
    def verify_confirmation_token(token, serializer, expires_sec=1800):
        """Verify a confirmation token and return the user object if valid."""
        try:
            data = serializer.loads(token, max_age=expires_sec)
        except Exception:
            return None
        return User.query.get(data.get('user_id'))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    status = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_file = db.Column(db.String(120), nullable=False, default='default_book.png')

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}')"

    @staticmethod
    def generate_dummy_books(users, num_books_per_user=5):
        """Generate dummy books for a list of users."""
        genres = [
            "Fiction", "Non-fiction", "Fantasy", "Science Fiction", "Mystery",
            "Thriller", "Biography", "History", "Horror", "Romance", "Poetry"
        ]
        statuses = ["read", "unread", "reading", "finished", "on-hold"]
        total_books_generated = 0

        dummy_images = [
            'book_1.png', 'book_2.png', 'book_3.png', 'book_4.png', 'book_5.png',
            'book_6.png', 'book_7.png', 'book_8.png', 'book_9.png', 'book_10.png'
        ]

        print(f"Generating books for {len(users)} users (~{len(users) * num_books_per_user} books)...")

        faker = Faker()
        for user in users:
            num_books = random.randint(1, num_books_per_user * 2)
            for _ in range(num_books):
                book = Book(
                    title=faker.sentence(nb_words=random.randint(3, 8)).rstrip('.'),
                    author=faker.name(),
                    genre=random.choice(genres),
                    status=random.choice(statuses),
                    user_id=user.id,
                    image_file=random.choice(dummy_images)
                )
                db.session.add(book)
                total_books_generated += 1

        db.session.commit()
        print(f"{total_books_generated} books generated.")