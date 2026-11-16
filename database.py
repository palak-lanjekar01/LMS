import mysql.connector
from werkzeug.security import generate_password_hash

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="palak",  # Change if your MySQL has a password
        database="libmatrix_db",
        autocommit=True
    )
    return conn

def init_db():
    # Step 1: Create database if not exists
    temp_conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="palak"
    )
    temp_cursor = temp_conn.cursor()
    temp_cursor.execute("CREATE DATABASE IF NOT EXISTS libmatrix_db")
    temp_cursor.close()
    temp_conn.close()

    # Step 2: Connect and create operational tables
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS administrators (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            isbn VARCHAR(50) UNIQUE NOT NULL,
            total_copies INT NOT NULL,
            available_copies INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS library_members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(50) NOT NULL,
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS circulation_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT,
            member_id INT,
            issue_date VARCHAR(50) NOT NULL,
            due_date VARCHAR(50),
            return_date VARCHAR(50),
            loan_status ENUM('Active', 'Returned', 'Overdue') DEFAULT 'Active',
            FOREIGN KEY (book_id) REFERENCES inventory_books (id) ON DELETE CASCADE,
            FOREIGN KEY (member_id) REFERENCES library_members (id) ON DELETE CASCADE
        )
    ''')
    
    # Seed default admin login
    cursor.execute('SELECT * FROM administrators WHERE username = %s', ('LMS',))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('lms@123')
        cursor.execute('INSERT INTO administrators (username, password) VALUES (%s, %s)', ('LMS', hashed_pw))
        
    cursor.close()
    conn.close()