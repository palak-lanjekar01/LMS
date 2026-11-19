# LibMatrix – Library Management System

<escape>🚀</escape> **Live Demo:** [Open LibMatrix](https://lms-jade-sigma-98.vercel.app/)

A modern Library Management System built using Python, Flask, MongoDB, HTML, CSS and Bootstrap.

# 📚 LibMatrix | Library Management System

A modern, full-stack, professional-grade Library Management System built with **Flask**, **MySQL**, and a sleek **Bootstrap 5** interface. Designed with a split-screen login portal, real-time inventory management, member directory, and a complete circulation desk for tracking book checkouts and returns.

---

## 🚀 Key Features

* **Modern Authentication Portal:** Split-screen administrator login interface with password visibility toggles and secure session management.
* **Real-Time Telemetry Dashboard:** Live metrics tracking total book inventory counts, registered library members, active checkouts, and recent circulation logs.
* **Inventory Catalog (`Books`):** Add, view, track total vs. available copies, manage ISBN records, and remove outdated stock.
* **Patron Directory (`Members`):** Register new library members and maintain contact details (name, email, phone).
* **Circulation Desk (`Issue / Return`):** Streamlined checkout system that validates book availability, calculates 14-day due dates, updates stock counts in real-time, and logs returns.
* **Responsive Dark Sidebar UI:** Fixed dark sidebar navigation layout built with custom CSS gradients and FontAwesome icons.

---

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, Werkzeug (Password Hashing & Security)
* **Database:** MySQL (`mysql-connector-python`)
* **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome Icons

---

## ⚙️ Prerequisites & Database Setup

Ensure you have **Python 3.x** and **MySQL Server** (via XAMPP, WAMP, or standalone MySQL) installed and running on your machine.

1. Start your MySQL service.
2. The application automatically creates the `libmatrix_db` database and all required tables (`administrators`, `inventory_books`, `library_members`, `circulation_logs`) when launched for the first time.

---

## 📥 Installation & Running Guide

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME.git
cd YOUR-REPOSITORY-NAME
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database Credentials (Optional)
If your local MySQL `root` account uses a password, open `database.py` and update the `password` field:
```python
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_mysql_password",
    database="libmatrix_db",
    autocommit=True
)
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Web App
Open your browser and visit:
```text
http://127.0.0.1:5000/
```

* **Default Administrator Credentials:**
  * **Username:** `LMS`
  * **Password:** `lms@123`

---

## 🗂️ Project Structure

```text
LibMatrix/
│
├── app.py                  # Main Flask application & routes
├── database.py             # MySQL connection & schema initializer
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
├── static/
│   └── style.css           # Custom UI styles, layout, and sidebar rules
│
└── templates/
    ├── base.html           # Layout wrapper (Sidebar, Navbar, Flash alerts)
    ├── login.html          # Split-screen login interface
    ├── dashboard.html      # Main telemetry dashboard & quick actions
    ├── books.html          # Inventory catalog management
    ├── students.html       # Member directory management
    └── issue.html          # Circulation desk (Issue & Return workflow)
```

---

## 📄 License

This project is open-source and available for educational and portfolio purposes.
