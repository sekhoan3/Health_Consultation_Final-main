import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "health_platform.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'patient',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date_of_birth TEXT,
            gender TEXT,
            phone TEXT,
            address TEXT,
            blood_type TEXT,
            allergies TEXT,
            emergency_contact TEXT,
            emergency_phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            specialty TEXT,
            license_number TEXT,
            phone TEXT,
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER,
            chief_complaint TEXT NOT NULL,
            symptoms TEXT,
            duration TEXT,
            severity TEXT,
            medical_history TEXT,
            current_medications TEXT,
            notes TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultation_id INTEGER,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            type TEXT DEFAULT 'in-person',
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consultation_id) REFERENCES consultations(id),
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)

    conn.commit()
    conn.close()


def seed_demo_data():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        import hashlib
        def hash_pw(pw):
            return hashlib.sha256(pw.encode()).hexdigest()

        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ("Admin", "admin@health.com", hash_pw("admin123"), "admin"))

        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ("Dr. Sarah Mitchell", "doctor@health.com", hash_pw("doctor123"), "doctor"))
        doctor_user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO doctors (user_id, specialty, license_number, phone, bio)
            VALUES (?, ?, ?, ?, ?)
        """, (doctor_user_id, "General Practitioner", "LIC-20241001", "+1-555-0100",
              "Experienced general practitioner with 12 years of clinical practice."))
        doctor_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ("John Doe", "patient@health.com", hash_pw("patient123"), "patient"))
        patient_user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO patients (user_id, date_of_birth, gender, phone, blood_type, allergies, emergency_contact, emergency_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_user_id, "1990-05-14", "Male", "+1-555-0200", "O+",
              "Penicillin", "Jane Doe", "+1-555-0201"))
        patient_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO consultations (patient_id, doctor_id, chief_complaint, symptoms, duration, severity, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, "Persistent headache", "Throbbing headache, light sensitivity", "3 days", "Moderate", "pending"))

        cursor.execute("""
            INSERT INTO consultations (patient_id, doctor_id, chief_complaint, symptoms, duration, severity, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, "Annual check-up", "No specific symptoms", "N/A", "Low", "completed"))

        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, type, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, "2026-08-25", "10:00", "in-person", "scheduled"))

        conn.commit()

    conn.close()
