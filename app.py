
import os
from datetime import datetime, timedelta

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from werkzeug.security import (
    check_password_hash, generate_password_hash
)

from database import (
    init_db,
    admins_collection,
    books_collection,
    students_collection,
    issued_books_collection,
    activity_logs_collection
)


# ==========================================
# FLASK CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_application():

    init_db()

    # Create the first administrator if one does not exist.
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "ADMIN_USERNAME or ADMIN_PASSWORD is missing from .env"
        )

    if not admins_collection.find_one({"username": username}):
        admins_collection.insert_one({
            "username": username,
            "password": generate_password_hash(password),
            "created_at": datetime.now()
        })

        print("Initial LibMatrix administrator created.")


initialize_application()


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def is_admin():
    return "admin_id" in session


def valid_object_id(value):
    try:
        return ObjectId(value)
    except Exception:
        return None


def add_activity(action, details):
    activity_logs_collection.insert_one({
        "admin_id": session.get("admin_id"),
        "action": action,
        "details": details,
        "created_at": datetime.now()
    })


def format_book(book):
    book["id"] = str(book["_id"])
    return book


def format_student(student):
    student["id"] = str(student["_id"])
    return student


def format_issue(record):
    record["id"] = str(record["_id"])
    record["issue_date"] = record["issue_date"].strftime("%Y-%m-%d")
    record["due_date"] = record["due_date"].strftime("%Y-%m-%d")

    if record.get("return_date"):
        record["return_date"] = record["return_date"].strftime("%Y-%m-%d")

    book = books_collection.find_one({"_id": record["book_id"]})
    student = students_collection.find_one({"_id": record["student_id"]})

    record["title"] = book["title"] if book else "Deleted Book"
    record["name"] = student["name"] if student else "Deleted Member"

    return record


# ==========================================
# HOME
# ==========================================

@app.route("/")
def index():

    if is_admin():
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if is_admin():
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = admins_collection.find_one({
            "username": username
        })

        if admin and check_password_hash(admin["password"], password):

            session.clear()
            session["admin_id"] = str(admin["_id"])
            session["username"] = admin["username"]

            flash("Successfully logged in!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "info")

    return redirect(url_for("login"))


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    if not is_admin():
        return redirect(url_for("login"))

    total_books = sum(
        book.get("total_copies", 0)
        for book in books_collection.find({}, {"total_copies": 1})
    )

    total_members = students_collection.count_documents({})

    active_loans = issued_books_collection.count_documents({
        "loan_status": "Active"
    })

    recent_activity = []

    records = issued_books_collection.find().sort(
        "_id", -1
    ).limit(5)

    for record in records:

        book = books_collection.find_one({
            "_id": record["book_id"]
        })

        student = students_collection.find_one({
            "_id": record["student_id"]
        })

        recent_activity.append({
            "title": book["title"] if book else "Deleted Book",
            "name": student["name"] if student else "Deleted Member",
            "issue_date": record["issue_date"].strftime("%Y-%m-%d"),
            "loan_status": record["loan_status"]
        })

    return render_template(
        "dashboard.html",
        total_books=total_books,
        total_members=total_members,
        active_loans=active_loans,
        recent_activity=recent_activity
    )


# ==========================================
# BOOK MANAGEMENT
# ==========================================

@app.route("/books", methods=["GET", "POST"])
def books():

    if not is_admin():
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()

        try:
            copies = int(request.form.get("copies", 0))

            if not title or not author or not isbn or copies < 1:
                raise ValueError

            books_collection.insert_one({
                "title": title,
                "author": author,
                "isbn": isbn,
                "total_copies": copies,
                "available_copies": copies,
                "created_at": datetime.now()
            })

            add_activity("Book Added", title)

            flash("Book successfully added to inventory!", "success")

        except ValueError:
            flash("Please enter valid book details and copies.", "danger")

        except DuplicateKeyError:
            flash("A book with this ISBN already exists.", "danger")

        return redirect(url_for("books"))

    inventory = [
        format_book(book)
        for book in books_collection.find().sort("created_at", -1)
    ]

    return render_template("books.html", books=inventory)


# ==========================================
# DELETE BOOK
# ==========================================

@app.route("/books/delete/<book_id>")
def delete_book(book_id):

    if not is_admin():
        return redirect(url_for("login"))

    object_id = valid_object_id(book_id)

    if not object_id:
        flash("Invalid book ID.", "danger")
        return redirect(url_for("books"))

    book = books_collection.find_one({"_id": object_id})

    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for("books"))

    active_issues = issued_books_collection.count_documents({
        "book_id": object_id,
        "loan_status": "Active"
    })

    if active_issues > 0:
        flash("Cannot delete a book that has active issues.", "danger")
        return redirect(url_for("books"))

    books_collection.delete_one({"_id": object_id})

    add_activity("Book Deleted", book["title"])

    flash("Book removed from inventory.", "success")

    return redirect(url_for("books"))


# ==========================================
# STUDENT / MEMBER MANAGEMENT
# ==========================================

@app.route("/students", methods=["GET", "POST"])
def students():

    if not is_admin():
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()

        if not name or not email or not phone:
            flash("Please complete all member details.", "danger")
            return redirect(url_for("students"))

        try:

            students_collection.insert_one({
                "name": name,
                "email": email,
                "phone": phone,
                "joined_date": datetime.now()
            })

            add_activity("Member Registered", name)

            flash("Member registered successfully!", "success")

        except DuplicateKeyError:
            flash("Email address is already registered.", "danger")

        return redirect(url_for("students"))

    members = [
        format_student(student)
        for student in students_collection.find().sort("joined_date", -1)
    ]

    return render_template("students.html", students=members)


# ==========================================
# DELETE MEMBER
# ==========================================

@app.route("/students/delete/<student_id>")
def delete_student(student_id):

    if not is_admin():
        return redirect(url_for("login"))

    object_id = valid_object_id(student_id)

    if not object_id:
        flash("Invalid member ID.", "danger")
        return redirect(url_for("students"))

    student = students_collection.find_one({"_id": object_id})

    if not student:
        flash("Member not found.", "danger")
        return redirect(url_for("students"))

    active_issues = issued_books_collection.count_documents({
        "student_id": object_id,
        "loan_status": "Active"
    })

    if active_issues > 0:
        flash("Cannot delete a member with active issued books.", "danger")
        return redirect(url_for("students"))

    students_collection.delete_one({"_id": object_id})

    add_activity("Member Deleted", student["name"])

    flash("Member removed successfully.", "success")

    return redirect(url_for("students"))


# ==========================================
# ISSUE BOOKS
# ==========================================

@app.route("/issue", methods=["GET", "POST"])
def issue_books():

    if not is_admin():
        return redirect(url_for("login"))

    if request.method == "POST":

        book_id = valid_object_id(request.form.get("book_id", ""))
        student_id = valid_object_id(request.form.get("member_id", ""))

        if not book_id or not student_id:
            flash("Invalid book or member selection.", "danger")
            return redirect(url_for("issue_books"))

        book = books_collection.find_one_and_update(
            {
                "_id": book_id,
                "available_copies": {"$gt": 0}
            },
            {
                "$inc": {"available_copies": -1}
            }
        )

        if not book:
            flash("Selected book is out of stock!", "danger")
            return redirect(url_for("issue_books"))

        student = students_collection.find_one({
            "_id": student_id
        })

        if not student:
            books_collection.update_one(
                {"_id": book_id},
                {"$inc": {"available_copies": 1}}
            )
            flash("Selected member does not exist.", "danger")
            return redirect(url_for("issue_books"))

        now = datetime.now()

        try:

            issued_books_collection.insert_one({
                "book_id": book_id,
                "student_id": student_id,
                "issue_date": now,
                "due_date": now + timedelta(days=14),
                "return_date": None,
                "loan_status": "Active"
            })

            add_activity("Book Issued", book["title"])

            flash("Book issued successfully!", "success")

        except Exception:

            # Restore the available copy if issuing fails.
            books_collection.update_one(
                {"_id": book_id},
                {"$inc": {"available_copies": 1}}
            )

            raise

        return redirect(url_for("issue_books"))

    available_books = [
        format_book(book)
        for book in books_collection.find({
            "available_copies": {"$gt": 0}
        })
    ]

    members = [
        format_student(student)
        for student in students_collection.find()
    ]

    circulation_records = [
        format_issue(record)
        for record in issued_books_collection.find().sort("_id", -1)
    ]

    return render_template(
        "issue.html",
        books=available_books,
        students=members,
        issued_records=circulation_records
    )


# ==========================================
# RETURN BOOK
# ==========================================

@app.route("/return/<record_id>")
def return_book(record_id):

    if not is_admin():
        return redirect(url_for("login"))

    object_id = valid_object_id(record_id)

    if not object_id:
        flash("Invalid circulation record.", "danger")
        return redirect(url_for("issue_books"))

    record = issued_books_collection.find_one({
        "_id": object_id,
        "loan_status": "Active"
    })

    if not record:
        flash("Active issue record not found.", "danger")
        return redirect(url_for("issue_books"))

    return_date = datetime.now()

    result = issued_books_collection.update_one(
        {
            "_id": object_id,
            "loan_status": "Active"
        },
        {
            "$set": {
                "loan_status": "Returned",
                "return_date": return_date
            }
        }
    )

    if result.modified_count == 1:

        books_collection.update_one(
            {"_id": record["book_id"]},
            {"$inc": {"available_copies": 1}}
        )

        add_activity("Book Returned", str(record["book_id"]))

        flash("Book returned successfully!", "success")

    return redirect(url_for("issue_books"))


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
