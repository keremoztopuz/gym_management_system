from flask import Flask, render_template, flash, redirect, request, session, url_for, jsonify
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-fallback-key')

DB_NAME = os.environ.get('DB_NAME', 'gym_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_latest_articles():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM articles ORDER BY create_date DESC LIMIT 3")
        articles = cur.fetchall()
        cur.close()
        conn.close()
        return articles
    return []

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    
    if request.method == 'POST' and form.validate():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = hashed_password
        weight = form.weight.data
        height = form.height.data
        location = form.location.data

        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, username, email, password, weight, height, city) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, username, email, password, weight, height, location)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('You have successfully registered', 'success')
            return redirect(url_for('login'))
        else:
            flash('Database connection error', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html', form=form, articles_data=get_latest_articles())

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        conn = get_db_connection()
        if conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM users WHERE email = %s", (form.email.data,))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user:
                if check_password_hash(user['password'], form.password.data):
                    flash('You have successfully logged in.', "success")
                    session['logged_in'] = True
                    session['email'] = user['email']
                    session['username'] = user['username']
                    return redirect('/')
                else:
                    flash('Username or Password Incorrect', "danger")
                    return redirect(url_for('login'))
            else:
                flash('Username or Password Incorrect', "danger")
                return redirect(url_for('login'))
        else:
            flash('Database connection error', "danger")
            return redirect(url_for('login'))
    
    return render_template('loginpage.html', form=form, articles_data=get_latest_articles())

@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect('/')

@app.route("/")
def homepage():
    return render_template("homepage.html", articles_data=get_latest_articles())

@app.route("/trainers")
def teachers():
    return render_template("trainers.html", articles_data=get_latest_articles())

@app.route("/clubs")
def clubs():
    return render_template("clubs.html", articles_data=get_latest_articles())

@app.route("/grouplessons")
def grouplessons():
    return render_template("grouplessons.html", articles_data=get_latest_articles())

@app.route("/edit-profile")
def edit_profile():
    return render_template("edit-profile.html", articles_data=get_latest_articles())

@app.route("/privacy")
def privacy():
    return render_template("privacy.html", articles_data=get_latest_articles())

@app.route('/api/trainers/<club_name>')
def get_trainers(club_name):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM trainers WHERE club_name = %s", (club_name,))
        trainers = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(trainers)
    return jsonify([])

@app.route('/api/lessons/<club_name>')
def get_lessons(club_name):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM group_lessons WHERE club_name = %s ORDER BY time_slot", (club_name,))
        lessons = cur.fetchall()
        cur.close()
        conn.close()
        
        grouped_lessons = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        for lesson in lessons:
            day = lesson['day_of_week']
            if day in grouped_lessons:
                grouped_lessons[day].append({
                    "title": lesson['title'],
                    "instructor": lesson['instructor'],
                    "time": lesson['time_slot'],
                    "capacity": lesson['capacity']
                })
        
        return jsonify(grouped_lessons)
    return jsonify({})

@app.route('/api/save_bmi', methods=['POST'])
def save_bmi():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    bmi = data.get('bmi')
    weight = data.get('weight')
    
    conn = get_db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id FROM users WHERE email = %s", (session['email'],))
        user = cur.fetchone()
        
        if user:
            cur.execute("INSERT INTO bmi_records (user_id, bmi, weight) VALUES (%s, %s, %s)", (user['id'], bmi, weight))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'message': 'BMI saved successfully'})
    return jsonify({'error': 'Database error'}), 500

@app.route('/api/get_bmi_history')
def get_bmi_history():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id FROM users WHERE email = %s", (session['email'],))
        user = cur.fetchone()
        
        if user:
            cur.execute("SELECT * FROM bmi_records WHERE user_id = %s ORDER BY recorded_at ASC", (user['id'],))
            records = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(records)
    return jsonify([])

@app.route('/api/reserve_lesson', methods=['POST'])
def reserve_lesson():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    
    conn = get_db_connection()
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id FROM users WHERE email = %s", (session['email'],))
        user = cur.fetchone()
        
        if user:
            cur.execute("""
                INSERT INTO reservations (user_id, lesson_title, lesson_time, lesson_day, club_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (user['id'], data['title'], data['time'], data['day'], data['club']))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'message': 'Reservation successful'})
    return jsonify({'error': 'Database error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)