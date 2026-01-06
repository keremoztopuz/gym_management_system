import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import random
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get('DB_NAME', 'gym_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

def get_db_connection(db_name=None):
    try:
        conn = psycopg2.connect(
            dbname=db_name if db_name else "postgres",
            user=DB_USER,
            host=DB_HOST,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_database():
    conn = get_db_connection()
    if not conn:
        return False
    
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database '{DB_NAME}' created successfully.")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{DB_NAME}' already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cur.close()
        conn.close()
    return True

def create_tables():
    conn = get_db_connection(DB_NAME)
    if not conn:
        return
    
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            username VARCHAR(100) UNIQUE,
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            city VARCHAR(50),
            gender VARCHAR(20),
            age INT,
            weight FLOAT,
            height FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trainers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            expertise VARCHAR(100),
            bio TEXT,
            image_url VARCHAR(255),
            club_name VARCHAR(100),
            age INT
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_lessons (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100),
            instructor VARCHAR(100),
            day_of_week VARCHAR(20),
            time_slot VARCHAR(20),
            club_name VARCHAR(100),
            capacity INT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clubs (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE,
            city VARCHAR(50)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            body TEXT,
            author VARCHAR(100),
            create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bmi_records (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id),
            bmi FLOAT,
            weight FLOAT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id),
            lesson_title VARCHAR(100),
            lesson_time VARCHAR(20),
            lesson_day VARCHAR(20),
            club_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Tables created successfully.")

def seed_data():
    conn = get_db_connection(DB_NAME)
    if not conn:
        return
    
    cur = conn.cursor()
    
    cur.execute("TRUNCATE TABLE trainers, group_lessons, clubs, articles, bmi_records, reservations RESTART IDENTITY;")
    
    CLUBS = {
        "ankara": ["Ankamall AVM", "Kentpark AVM", "Cepa AVM", "Armada AVM", "Metromall AVM"],
        "izmir": ["Balçova Kipa", "Kidsmall", "Gaziemir Optimum", "Kıbrıs Şehitleri", "Ege Perla"],
        "istanbul": ["Zorlu AVM", "Ömür Plaza", "FlyInn", "İstiklal AVM", "Marmara Park"]
    }
    
    TRAINER_NAMES = [
        "John Doe", "Jane Smith", "Michael Johnson", "Emily Davis", "Chris Brown",
        "Sarah Wilson", "David Taylor", "Laura Moore", "James Anderson", "Linda Thomas",
        "Robert Jackson", "Patricia White", "Charles Harris", "Jennifer Martin", "Daniel Thompson",
        "Elizabeth Garcia", "Matthew Martinez", "Barbara Robinson", "Anthony Clark", "Susan Rodriguez"
    ]
    
    CLASS_TYPES = [
        ("Yoga", "Mind & Body"), ("Pilates", "Core Strength"), ("HIIT", "Cardio"),
        ("Zumba", "Dance"), ("Spinning", "Cardio"), ("CrossFit", "Strength"),
        ("Boxing", "Combat"), ("Swimming", "Aquatic")
    ]
    
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    TIMES = ["07:00", "08:00", "09:00", "10:00", "12:00", "14:00", "16:00", "17:00", "18:00", "19:00", "20:00"]

    articles = [
        ("Summer Shredding", "Get ready for summer with this 4-week program designed to burn fat and build lean muscle.", "admin"),
        ("Nutrition 101", "Basic nutrition tips for muscle growth. Learn about macros, micros, and timing your meals.", "admin"),
        ("Yoga for Beginners", "Start your journey to flexibility and peace. A guide to the most essential poses.", "admin"),
        ("The Benefits of HIIT", "Why High Intensity Interval Training is the most efficient way to burn calories.", "admin"),
        ("Recovery Techniques", "How to recover faster after a heavy workout using foam rolling and stretching.", "admin")
    ]

    for title, body, author in articles:
        cur.execute("INSERT INTO articles (title, body, author) VALUES (%s, %s, %s)", (title, body, author))

    for city, club_list in CLUBS.items():
        for club_name in club_list:
            cur.execute("INSERT INTO clubs (name, city) VALUES (%s, %s)", (club_name, city))
            
            num_trainers = random.randint(12, 13)
            for _ in range(num_trainers):
                name = random.choice(TRAINER_NAMES)
                expertise = random.choice(CLASS_TYPES)[0]
                age = random.randint(20, 40)
                max_experience = max(0, age - 18)
                experience = random.randint(1, max_experience) if max_experience > 1 else 1
                bio = f"Certified {expertise} trainer with {experience} years of experience."
                image_url = "https://randomuser.me/api/portraits/men/" + str(random.randint(1, 99)) + ".jpg" if random.random() > 0.5 else "https://randomuser.me/api/portraits/women/" + str(random.randint(1, 99)) + ".jpg"
                
                cur.execute("""
                    INSERT INTO trainers (name, expertise, bio, image_url, club_name, age)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, expertise, bio, image_url, club_name, age))
            
            for day in DAYS:
                num_lessons = random.randint(15, 20)
                for _ in range(num_lessons):
                    lesson_type = random.choice(CLASS_TYPES)[0]
                    instructor = random.choice(TRAINER_NAMES)
                    time_slot = random.choice(TIMES)
                    capacity = random.randint(15, 30)
                    
                    cur.execute("""
                        INSERT INTO group_lessons (title, instructor, day_of_week, time_slot, club_name, capacity)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (lesson_type, instructor, day, time_slot, club_name, capacity))

    conn.commit()
    cur.close()
    conn.close()
    print("Data seeded successfully.")

if __name__ == "__main__":
    print("Setting up PostgreSQL database...")
    if create_database():
        create_tables()
        seed_data()
        print("Setup complete.")
