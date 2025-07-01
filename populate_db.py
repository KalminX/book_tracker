# populate_db.py
import json
import os
import random
import time
from werkzeug.security import generate_password_hash
from faker import Faker

# IMPORTANT: Ensure 'app' and 'db' are correctly initialized in app.py or a factory function
# before this script is run. This import assumes your app.py correctly sets them up.
from app import app, db
from models import User, Book

# --- Configuration ---
USER_DATA_FILE = 'usernames.json'
COMMON_PASSWORD = 'password'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin_password' # Ensure this matches your login attempt for admin

# --- Main script to populate the database ---
def populate_database(num_books_per_user=5):
    """
    Orchestrates the dummy data generation. It will drop tables
    if the app is in debug mode (allowing for fresh starts).
    """
    start_time = time.time()
    print(f"[{time.time() - start_time:.2f}s] --- Starting Database Population Script ---")

    with app.app_context():
        # --- Safety Check: Prevent dropping tables in production or with existing data ---
        print(f"[{time.time() - start_time:.2f}s] Checking database population status...")
        is_database_populated = User.query.first() is not None

        if is_database_populated and not app.debug:
            print("=" * 50)
            print("WARNING: Database contains data and app is not in debug mode.")
            print("Database population is disabled to prevent data loss in production.")
            print("To re-populate, enable debug mode or delete the database file.")
            print("=" * 50)
            return

        # Always drop tables if debug mode is on, to ensure a clean slate for development
        if app.debug:
            try:
                print(f"[{time.time() - start_time:.2f}s] Attempting to drop existing database tables (in debug mode)...")
                db.drop_all()
                print(f"[{time.time() - start_time:.2f}s] Database tables dropped successfully.")
            except Exception as e:
                print(f"[{time.time() - start_time:.2f}s] ERROR: Could not drop tables. This might indicate a problem or non-existent tables: {e}")
        else:
            print(f"[{time.time() - start_time:.2f}s] Not in debug mode. Will not drop tables if data exists.")
        
        print(f"[{time.time() - start_time:.2f}s] Creating database tables...")
        db.create_all()
        print(f"[{time.time() - start_time:.2f}s] Database tables created successfully.")

        # --- Population Logic ---
        users_to_add_to_session = []

        # 1. Create Admin User (and commit immediately)
        print(f"[{time.time() - start_time:.2f}s] Creating admin user: {ADMIN_USERNAME}...")
        admin_email = "numzykalmin@gmail.com" # Consider making this dynamic or a config variable
        admin_user = User(username=ADMIN_USERNAME, email=admin_email,
                          password_hash=generate_password_hash(ADMIN_PASSWORD),
                          confirmed=True)
        db.session.add(admin_user)
        print(f"[{time.time() - start_time:.2f}s] Committing admin user...")
        db.session.commit()
        print(f"[{time.time() - start_time:.2f}s] Admin user '{ADMIN_USERNAME}' created and committed.")

        # 2. Read other users from JSON
        print(f"[{time.time() - start_time:.2f}s] Attempting to load users from {USER_DATA_FILE}...")
        if os.path.exists(USER_DATA_FILE):
            try:
                with open(USER_DATA_FILE, 'r') as f:
                    json_usernames = json.load(f)
                print(f"[{time.time() - start_time:.2f}s] Successfully loaded {len(json_usernames)} usernames from {USER_DATA_FILE}.")

                # --- OPTIMIZATION START ---
                # Fetch all existing usernames and emails into sets ONCE
                # Note: After a db.drop_all(), these sets will be empty initially.
                print(f"[{time.time() - start_time:.2f}s] Fetching existing usernames and emails for faster checks...")
                existing_usernames = {u.username for u in User.query.with_entities(User.username).all()}
                existing_emails = {u.email for u in User.query.with_entities(User.email).all()}
                print(f"[{time.time() - start_time:.2f}s] Found {len(existing_usernames)} existing usernames and {len(existing_emails)} existing emails.")

                num_added = 0
                processed_count = 0
                total_json_users = len(json_usernames)

                print(f"[{time.time() - start_time:.2f}s] Starting user processing loop ({total_json_users} users)...")
                for username in json_usernames:
                    processed_count += 1
                    if processed_count % 100 == 0: # Log progress every 100 users
                        print(f"[{time.time() - start_time:.2f}s]   Processed {processed_count}/{total_json_users} JSON users...")

                    if username == ADMIN_USERNAME:
                        continue # Skip if username is the same as admin username
                    
                    if username in existing_usernames:
                        # print(f"[{time.time() - start_time:.2f}s] Skipping '{username}', username already exists.")
                        continue

                    # Generate a unique email based on the username
                    first_name_part = username.split('.')[0].replace('-', '').lower() # Handle potential hyphens
                    base_email = f"{first_name_part}@example.com" # Use a generic domain
                    
                    user_email = base_email
                    counter = 1
                    while user_email in existing_emails:
                        user_email = f"{first_name_part}{counter}@example.com"
                        counter += 1
                    
                    existing_emails.add(user_email) # Add to the set to prevent duplicates in current run

                    hashed_password = generate_password_hash(COMMON_PASSWORD)
                    new_user = User(username=username, email=user_email,
                                    password_hash=hashed_password, confirmed=True) # Set confirmed to True for dummy users
                    
                    # No need to append to users_to_add_to_session if directly adding to db.session
                    db.session.add(new_user)
                    num_added += 1
                    
                print(f"[{time.time() - start_time:.2f}s] Finished processing JSON users. About to commit {num_added} new users...")
                db.session.commit() # Commit all the new users in a single batch
                print(f"[{time.time() - start_time:.2f}s] Successfully committed {num_added} new users from JSON.")

            except json.JSONDecodeError as e:
                print(f"[{time.time() - start_time:.2f}s] ERROR: Could not decode JSON from {USER_DATA_FILE}. Check file format. Error: {e}")
                db.session.rollback()
            except Exception as e:
                print(f"[{time.time() - start_time:.2f}s] ERROR: An unexpected error occurred while processing JSON users: {e}")
                db.session.rollback()
                
        else:
            print(f"[{time.time() - start_time:.2f}s] WARNING: {USER_DATA_FILE} not found. No JSON users will be added.")

        # 3. Generate books for all created users (including admin)
        # Fetch users again to ensure all new users (from JSON batch) are included
        print(f"[{time.time() - start_time:.2f}s] Querying all committed users for book generation...")
        all_committed_users = User.query.all() 
        print(f"[{time.time() - start_time:.2f}s] Found {len(all_committed_users)} users for book generation.")

        print(f"[{time.time() - start_time:.2f}s] Starting book generation for {len(all_committed_users)} users...")
        Book.generate_dummy_books(users=all_committed_users, num_books_per_user=num_books_per_user)
        print(f"[{time.time() - start_time:.2f}s] Book generation completed.")

        print(f"\n[{time.time() - start_time:.2f}s] --- Verification Summary ---")
        total_users = User.query.count()
        total_books = Book.query.count()
        print(f"[{time.time() - start_time:.2f}s] Total Users in DB: {total_users}")
        print(f"[{time.time() - start_time:.2f}s] Total Books in DB: {total_books}")
        
        print(f"[{time.time() - start_time:.2f}s] Database populated successfully! Total time: {time.time() - start_time:.2f}s")
        print("--- Finished ---")

if __name__ == '__main__':
    populate_database(num_books_per_user=7)