# Book Tracker

A Flask-based web app for tracking your personal library and reading progress. Add books with cover images, organize them by status, and manage your account with email confirmation and password reset.

## Features

- User registration and login
- Email confirmation and password reset flows
- Add / edit / delete books
- Upload book cover images (with validation and a default placeholder)
- Filter books by reading status (read, unread, reading, finished, on-hold)
- Dashboard-style counts and progress percentage

## Tech stack

- Python
- Flask
- SQLAlchemy + Flask-Migrate (Alembic)
- Flask-Login
- Flask-Mail
- PostgreSQL in production (e.g., Heroku), SQLite locally
- HTML templates + static assets
- Docker + Procfile for deployment

## Run locally

### 1) Create a virtualenv and install dependencies

```bash
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 2) Set environment variables

At minimum you should set:

- `SECRET_KEY`
- `DATABASE_URI` (or whatever your `config.py` expects)
- Mail settings if you want email flows (`MAIL_SERVER`, `MAIL_PORT`, etc.)

### 3) Initialize the database

```bash
flask db init
flask db migrate -m "Initial"
flask db upgrade
```

### 4) Start the app

```bash
flask run
```

Then open `http://127.0.0.1:5000`.

## Docker

```bash
docker build -t book-tracker .
docker run -p 5000:5000 book-tracker
```

## Deployment

This repo includes a `Procfile` for running with gunicorn (commonly used on Heroku-style platforms).

## License

Add a license file if you plan to distribute this project.