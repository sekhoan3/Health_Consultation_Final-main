import hashlib
from backend.database import get_db


def get_all_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.full_name, u.email, u.role, u.created_at,
               CASE
                 WHEN u.role = 'patient' THEN p.phone
                 WHEN u.role = 'doctor'  THEN d.phone
                 ELSE NULL
               END AS phone
        FROM users u
        LEFT JOIN patients p ON p.user_id = u.id
        LEFT JOIN doctors  d ON d.user_id = u.id
        ORDER BY u.created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_by_id(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_role(user_id: int, new_role: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()


def delete_user(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients      WHERE user_id = ?",       (user_id,))
    cur.execute("DELETE FROM doctors       WHERE user_id = ?",       (user_id,))
    cur.execute("DELETE FROM appointments  WHERE patient_id IN (SELECT id FROM patients WHERE user_id = ?)", (user_id,))
    cur.execute("DELETE FROM consultations WHERE patient_id IN (SELECT id FROM patients WHERE user_id = ?)", (user_id,))
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def create_user_by_admin(full_name: str, email: str, password: str, role: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return None, "Email already in use."
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    cur.execute(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (full_name, email, pw_hash, role),
    )
    user_id = cur.lastrowid
    if role == "patient":
        cur.execute("INSERT INTO patients (user_id) VALUES (?)", (user_id,))
    elif role == "doctor":
        cur.execute("INSERT INTO doctors (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return user_id, None


def get_admin_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'patient'")
    total_patients = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
    total_doctors = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    total_admins = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM consultations")
    total_consultations = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM consultations WHERE status = 'pending'")
    pending_consultations = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM consultations WHERE status = 'completed'")
    completed_consultations = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments WHERE status = 'scheduled'")
    scheduled_appointments = cur.fetchone()[0]

    cur.execute("""
        SELECT u.full_name, u.role, u.created_at
        FROM users u ORDER BY u.created_at DESC LIMIT 5
    """)
    recent_users = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT c.chief_complaint, c.status, c.severity, c.created_at,
               up.full_name AS patient_name
        FROM consultations c
        JOIN patients p ON c.patient_id = p.id
        JOIN users up ON p.user_id = up.id
        ORDER BY c.created_at DESC LIMIT 5
    """)
    recent_consultations = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "total_users": total_users,
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_admins": total_admins,
        "total_consultations": total_consultations,
        "pending_consultations": pending_consultations,
        "completed_consultations": completed_consultations,
        "total_appointments": total_appointments,
        "scheduled_appointments": scheduled_appointments,
        "recent_users": recent_users,
        "recent_consultations": recent_consultations,
    }


def assign_doctor_to_consultation(consultation_id: int, doctor_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE consultations SET doctor_id = ?, status = 'in-review', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (doctor_id, consultation_id),
    )
    conn.commit()
    conn.close()


def update_appointment_status(appointment_id: int, status: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()


def get_all_doctors_simple():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id, u.full_name, d.specialty
        FROM doctors d JOIN users u ON d.user_id = u.id
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
