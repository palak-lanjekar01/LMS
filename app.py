from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import get_db_connection, init_db
from datetime import datetime, timedelta
import mysql.connector

app = Flask(__name__)
app.secret_key = 'libmatrix_live_production_key'

init_db()

@app.route('/')
def index():
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM administrators WHERE username = %s', (username,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['id']
            session['username'] = admin['username']
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT SUM(total_copies) AS total FROM inventory_books')
    res_books = cursor.fetchone()
    total_books = res_books['total'] if res_books and res_books['total'] else 0
    
    cursor.execute('SELECT COUNT(*) AS total FROM library_members')
    res_members = cursor.fetchone()
    total_members = res_members['total'] if res_members else 0
    
    cursor.execute("SELECT COUNT(*) AS total FROM circulation_logs WHERE loan_status = 'Active'")
    res_active = cursor.fetchone()
    active_loans = res_active['total'] if res_active else 0
    
    cursor.execute('''
        SELECT c.id, b.title, m.name, c.issue_date, c.loan_status 
        FROM circulation_logs c
        JOIN inventory_books b ON c.book_id = b.id
        JOIN library_members m ON c.member_id = m.id
        ORDER BY c.id DESC LIMIT 5
    ''')
    recent_activity = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', total_books=total_books, total_members=total_members, active_loans=active_loans, recent_activity=recent_activity)

@app.route('/books', methods=['GET', 'POST'])
def books():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        copies = int(request.form['copies'])
        
        try:
            cursor.execute('''
                INSERT INTO inventory_books (title, author, isbn, total_copies, available_copies) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (title, author, isbn, copies, copies))
            flash('Book successfully added to inventory!', 'success')
        except mysql.connector.IntegrityError:
            flash('A book with this ISBN already exists.', 'danger')
            
        cursor.close()
        conn.close()
        return redirect(url_for('books'))
        
    cursor.execute('SELECT * FROM inventory_books')
    inventory = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('books.html', books=inventory)

@app.route('/books/delete/<int:book_id>')
def delete_book(book_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM inventory_books WHERE id = %s', (book_id,))
    cursor.close()
    conn.close()
    flash('Book removed from inventory.', 'success')
    return redirect(url_for('books'))

@app.route('/students', methods=['GET', 'POST'])
def students():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        try:
            cursor.execute('INSERT INTO library_members (name, email, phone) VALUES (%s, %s, %s)', (name, email, phone))
            flash('Member registered successfully!', 'success')
        except mysql.connector.IntegrityError:
            flash('Email address is already registered.', 'danger')
            
        cursor.close()
        conn.close()
        return redirect(url_for('students'))
        
    cursor.execute('SELECT * FROM library_members')
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('students.html', students=members)

@app.route('/students/delete/<int:student_id>')
def delete_student(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM library_members WHERE id = %s', (student_id,))
    cursor.close()
    conn.close()
    flash('Member removed successfully.', 'success')
    return redirect(url_for('students'))

@app.route('/issue', methods=['GET', 'POST'])
def issue_books():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        
        cursor.execute('SELECT available_copies FROM inventory_books WHERE id = %s', (book_id,))
        book = cursor.fetchone()
        
        if book and book['available_copies'] > 0:
            issue_date = datetime.now().strftime('%Y-%m-%d')
            due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO circulation_logs (book_id, member_id, issue_date, due_date, loan_status) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (book_id, member_id, issue_date, due_date, 'Active'))
            
            cursor.execute('UPDATE inventory_books SET available_copies = available_copies - 1 WHERE id = %s', (book_id,))
            flash('Book issued successfully!', 'success')
        else:
            flash('Selected book is out of stock!', 'danger')
            
        cursor.close()
        conn.close()
        return redirect(url_for('issue_books'))
        
    cursor.execute('SELECT * FROM inventory_books WHERE available_copies > 0')
    available_books = cursor.fetchall()
    
    cursor.execute('SELECT * FROM library_members')
    members = cursor.fetchall()
    
    cursor.execute('''
        SELECT c.id, b.title, m.name, c.issue_date, c.due_date, c.return_date, c.loan_status 
        FROM circulation_logs c
        JOIN inventory_books b ON c.book_id = b.id
        JOIN library_members m ON c.member_id = m.id
    ''')
    circulation_records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('issue.html', books=available_books, students=members, issued_records=circulation_records)

@app.route('/return/<int:record_id>')
def return_book(record_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM circulation_logs WHERE id = %s', (record_id,))
    record = cursor.fetchone()
    
    if record and record['loan_status'] == 'Active':
        return_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('UPDATE circulation_logs SET loan_status = %s, return_date = %s WHERE id = %s', ('Returned', return_date, record_id))
        cursor.execute('UPDATE inventory_books SET available_copies = available_copies + 1 WHERE id = %s', (record['book_id'],))
        flash('Book returned successfully!', 'success')
        
    cursor.close()
    conn.close()
    return redirect(url_for('issue_books'))

if __name__ == '__main__':
    app.run(debug=True)