from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DB initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            password TEXT,
            image_path TEXT,
            address TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/home')
def home_page():
    return render_template('index.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = user[1]           # name
            session['user_image'] = user[4]     # image_path
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        image = request.files['image']

        # Save uploaded image
        image_path = ''
        if image:
            filename = image.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        # Save data to DB
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, password, image_path, address) VALUES (?, ?, ?, ?, ?)",
                  (name, email, password, image_path, address))
        conn.commit()
        conn.close()

        flash('Registered successfully! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/dashboard')
def dashboard():
    user_name = session.get('user', 'Guest')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT image_path, address FROM users WHERE name = ?", (user_name,))
    row = c.fetchone()
    conn.close()

    user_image = row[0] if row else "/static/default.png"
    user_address = row[1] if row else "No address found"

    return render_template('dashboard.html',
                           user_name=user_name,
                           user_image=user_image,
                           user_address=user_address)


if __name__ == '__main__':
    app.run(debug=True)
