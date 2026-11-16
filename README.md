# Library Management System (LBS)

A web-based Library Management System built with **Python (Flask)** and **MySQL**. Designed with a clean, responsive administrative interface to manage book inventory, student memberships, book circulation, and automated overdue fine calculations.

---

## Features

- **Admin Authentication:** Secure login and session management with hashed passwords (`Werkzeug`) and automated default admin initialization.
- **Dashboard Overview:** Real-time metrics displaying total catalog titles, available copies on shelf, active book loans, and registered students.
- **Books Catalog Management:** Add new books with stock quantities, search/filter by title or author, and safely delete unissued titles.
- **Students Directory:** Register student members with class/department, mobile, and email records, with validation preventing deletion of members holding unreturned books.
- **Circulation & Fine Automation:**
  - Issue available books to students with an automatic **14-day due date**.
  - Prevents duplicate active loans of the same book to the same student using database transactions (`FOR UPDATE`).
  - Automatic late fine calculation (**₹5/day**) for overdue returns.
  - Complete audit log of recent book returns and fines collected.

---

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** MySQL (`mysql-connector-python` / `PyMySQL`)
- **Frontend:** HTML5, Jinja2 Templates, Custom CSS
- **Security:** `python-dotenv`, `werkzeug.security`

---

## Project Structure

```text
library-management-system/
├── app.py                  # Main Flask application & routes
├── database.py             # MySQL database connection helper
├── requirements.txt        # Python dependencies
├── .gitignore              # Ignored files (venv, .env, cache)
├── static/
│   └── style.css           # Application stylesheet
└── templates/
    ├── base.html           # Master layout & navigation bar
    ├── login.html          # Admin login screen
    ├── dashboard.html      # KPI overview & quick actions
    ├── books.html          # Catalog management & search
    ├── students.html       # Student directory
    └── issue.html          # Book issue, return & fine tracking
```

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and configure your MySQL and Flask credentials:
```env
SECRET_KEY=your_secret_key_here
ADMIN_PASSWORD=Admin@123
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=library_db
```

### 5. Database Schema (MySQL)
Ensure your MySQL database contains the required tables (`users`, `books`, `students`, `issued_books`):

```sql
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    quantity INT NOT NULL DEFAULT 0
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    mobile VARCHAR(20),
    class_name VARCHAR(100)
);

CREATE TABLE issued_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    student_id INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    status ENUM('Issued', 'Returned') DEFAULT 'Issued',
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

### 6. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## Default Login Credentials

- **Username:** `LMS`
- **Password:** `lms@123` *(or the value set in `ADMIN_PASSWORD` inside `.env`)*
