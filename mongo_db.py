from urllib.parse import quote_plus
import os
from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv

# Find .env in the same folder as this Python file
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)

MONGODB_URI = os.getenv("MONGODB_URI")

if MONGODB_URI:
    # Encode username and password special characters
    prefix, remainder = MONGODB_URI.split("://", 1)

    if "@" in remainder:
        credentials, host = remainder.rsplit("@", 1)
        username, password = credentials.split(":", 1)

        username = quote_plus(username)
        password = quote_plus(password)

        MONGODB_URI = (
            f"{prefix}://{username}:{password}@{host}"
        )
MONGODB_DB = os.getenv("MONGODB_DB", "libmatrix_db")

if not MONGODB_URI:
    raise RuntimeError(
        f"MONGODB_URI is missing. Checked: {ENV_FILE}"
    )

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000
)

db = client[MONGODB_DB]


def test_connection():
    try:
        client.admin.command("ping")

        print("================================")
        print(" LIBMATRIX MONGODB CONNECTION")
        print("================================")
        print("Status: Connected successfully")
        print(f"Database: {MONGODB_DB}")
        print("Server: MongoDB Atlas")
        print("================================")

        return True

    except Exception as error:
        print("MongoDB connection failed!")
        print("Error:", error)
        return False

from pymongo import ASCENDING, DESCENDING


def setup_database():

    print("\nSetting up LibMatrix database...")

    # 1. ADMINS
    db.admins.create_index(
        [("username", ASCENDING)],
        unique=True
    )

    db.admins.create_index(
        [("email", ASCENDING)],
        unique=True,
        sparse=True
    )

    # 2. BOOKS
    db.books.create_index(
        [("isbn", ASCENDING)],
        unique=True,
        sparse=True
    )

    db.books.create_index(
        [("title", ASCENDING)]
    )

    db.books.create_index(
        [("category", ASCENDING)]
    )

    # 3. STUDENTS
    db.students.create_index(
        [("student_id", ASCENDING)],
        unique=True,
        sparse=True
    )

    db.students.create_index(
        [("email", ASCENDING)],
        unique=True,
        sparse=True
    )

    # 4. ISSUED BOOKS
    db.issued_books.create_index(
        [("student_id", ASCENDING)]
    )

    db.issued_books.create_index(
        [("book_id", ASCENDING)]
    )

    db.issued_books.create_index(
        [("status", ASCENDING)]
    )

    db.issued_books.create_index(
        [("due_date", ASCENDING)]
    )

    # 5. FINES
    db.fines.create_index(
        [("student_id", ASCENDING)]
    )

    db.fines.create_index(
        [("status", ASCENDING)]
    )

    # 6. ACTIVITY LOGS
    db.activity_logs.create_index(
        [("created_at", DESCENDING)]
    )

    db.activity_logs.create_index(
        [("admin_id", ASCENDING)]
    )

    print("\n================================")
    print(" LIBMATRIX DATABASE READY")
    print("================================")

    print("Collections and indexes created:")
    print("1. admins")
    print("2. books")
    print("3. students")
    print("4. issued_books")
    print("5. fines")
    print("6. activity_logs")

    print("\nDatabase setup completed successfully!")


if __name__ == "__main__":
    if test_connection():
        setup_database()
    else:
        print("Database setup cancelled. Check your MongoDB connection.")
