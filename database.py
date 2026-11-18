
from mongo_db import db, setup_database

# MongoDB collections
admins_collection = db["admins"]
books_collection = db["books"]
students_collection = db["students"]
issued_books_collection = db["issued_books"]
fines_collection = db["fines"]
activity_logs_collection = db["activity_logs"]


def init_db():
    """Initialize MongoDB collections and indexes."""
    setup_database()
    print("LibMatrix MongoDB database initialized successfully.")


def get_database():
    """Return the MongoDB database."""
    return db
