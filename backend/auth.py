import hashlib
from backend.database import get_db


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def register_user(full_name: str, email: str, password: str, role: str = "patient"):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return None, "An account with this email already exists."

    password_hash = hash_password(password)
    cursor.execute("""
        INSERT INTO users (full_name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    """, (full_name, email, password_hash, role))
    user_id = cursor.lastrowid

    if role == "patient":
        cursor.execute("INSERT INTO patients (user_id) VALUES (?)", (user_id,))
    elif role == "doctor":
        cursor.execute("INSERT INTO doctors (user_id) VALUES (?)", (user_id,))

    conn.commit()
    conn.close()
    return user_id, None


def login_user(email: str, password: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None, "No account found with this email address."

    if not verify_password(password, user["password_hash"]):
        return None, "Incorrect password. Please try again."

    return dict(user), None
