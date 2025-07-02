# Book Tracker App

A personal book management web application built with Flask.  
Track your reading progress, manage your book collection, upload cover images, and stay organized with ease.

---

## Demo

Try the live app here: [https://kal-book-app-ab180bb075cb.herokuapp.com/]

---

## Features

- User registration, login, email confirmation, and password reset  
- Add, edit, and delete books with cover images  
- Filter books by reading status (read, unread, reading, finished, on-hold)  
- Upload book cover images with validation and default placeholders  
- Secure authentication with password hashing  
- Email confirmation and password reset via secure tokens  
- Responsive and user-friendly interface  

---

## Tech Stack

- Python 3.10+  
- Flask web framework  
- Flask-Login for user sessions  
- Flask-Mail for email integration  
- SQLAlchemy as ORM  
- Alembic for database migrations  
- PostgreSQL (on Heroku) as the production database  
- WTForms / HTML forms for input  
- Bootstrap (or your choice) for styling  

---

## Installation

### Prerequisites

- Python 3.10+  
- PostgreSQL (or use Heroku Postgres)  
- Git  

### Clone the repository

```bash
git clone https://github.com/yourusername/book_tracker.git
cd book_tracker
````

### Create a virtual environment and activate it

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set up environment variables

Create a `.env` file (or set environment variables) with the following variables:

```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URI=postgresql://username:password@localhost/dbname
SECRET_KEY=your_secret_key
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
```

### Initialize the database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## Running the app locally

```bash
flask run
```

The app will be available at `http://127.0.0.1:5000`

---

## Deployment

This app can be deployed to Heroku easily with PostgreSQL add-on enabled. After pushing to Heroku, run:

```bash
heroku run flask db upgrade --app your-heroku-app-name
```

to apply migrations.

---

## Folder Structure

```
book_tracker/
│
├── app.py               # Main Flask application
├── models.py            # Database models (User, Book)
├── utils.py             # Helper functions (image upload, email)
├── migrations/          # Alembic migrations folder
├── templates/           # HTML templates
├── static/              # Static files (CSS, images)
├── requirements.txt     # Python dependencies
└── config.py            # App factory and configuration
```

---

## Contributing

Contributions are welcome! Please fork the repo and create a pull request with improvements.

---

## License

MIT License © 2025 Kalmin

---
