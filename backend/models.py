from backend.database import get_db


def get_patient_by_user_id(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, u.full_name, u.email
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_patient_profile(user_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patients SET
            date_of_birth = ?,
            gender = ?,
            phone = ?,
            address = ?,
            blood_type = ?,
            allergies = ?,
            emergency_contact = ?,
            emergency_phone = ?
        WHERE user_id = ?
    """, (
        data.get("date_of_birth"),
        data.get("gender"),
        data.get("phone"),
        data.get("address"),
        data.get("blood_type"),
        data.get("allergies"),
        data.get("emergency_contact"),
        data.get("emergency_phone"),
        user_id,
    ))
    conn.commit()
    conn.close()


def update_doctor_profile(user_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE doctors SET
            specialty = ?,
            license_number = ?,
            phone = ?,
            bio = ?
        WHERE user_id = ?
    """, (
        data.get("specialty"),
        data.get("license_number"),
        data.get("phone"),
        data.get("bio"),
        user_id,
    ))
    conn.commit()
    conn.close()


def get_doctor_by_user_id(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.*, u.full_name, u.email
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_doctors():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.specialty, u.full_name, u.email
        FROM doctors d
        JOIN users u ON d.user_id = u.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_consultation(patient_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO consultations
            (patient_id, chief_complaint, symptoms, duration, severity, medical_history, current_medications, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (
        patient_id,
        data.get("chief_complaint"),
        data.get("symptoms"),
        data.get("duration"),
        data.get("severity"),
        data.get("medical_history"),
        data.get("current_medications"),
        data.get("notes"),
    ))
    conn.commit()
    consultation_id = cursor.lastrowid
    conn.close()
    return consultation_id


def get_consultations_by_patient(patient_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, u.full_name AS doctor_name
        FROM consultations c
        LEFT JOIN doctors d ON c.doctor_id = d.id
        LEFT JOIN users u ON d.user_id = u.id
        WHERE c.patient_id = ?
        ORDER BY c.created_at DESC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_consultations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, up.full_name AS patient_name, ud.full_name AS doctor_name
        FROM consultations c
        JOIN patients p ON c.patient_id = p.id
        JOIN users up ON p.user_id = up.id
        LEFT JOIN doctors d ON c.doctor_id = d.id
        LEFT JOIN users ud ON d.user_id = ud.id
        ORDER BY c.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_consultation_by_id(consultation_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, up.full_name AS patient_name, ud.full_name AS doctor_name
        FROM consultations c
        JOIN patients p ON c.patient_id = p.id
        JOIN users up ON p.user_id = up.id
        LEFT JOIN doctors d ON c.doctor_id = d.id
        LEFT JOIN users ud ON d.user_id = ud.id
        WHERE c.id = ?
    """, (consultation_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_consultation_status(consultation_id: int, status: str, notes: str = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE consultations SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, notes, consultation_id))
    conn.commit()
    conn.close()


def update_appointment_status(appointment_id: int, status: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE appointments SET status = ? WHERE id = ?",
        (status, appointment_id)
    )
    conn.commit()
    conn.close()


def create_appointment(patient_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, type, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        data.get("doctor_id"),
        data.get("appointment_date"),
        data.get("appointment_time"),
        data.get("type", "in-person"),
        data.get("notes"),
    ))
    conn.commit()
    appointment_id = cursor.lastrowid
    conn.close()
    return appointment_id


def get_appointments_by_patient(patient_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, ud.full_name AS doctor_name, d.specialty
        FROM appointments a
        LEFT JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN users ud ON d.user_id = ud.id
        WHERE a.patient_id = ?
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_appointments():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, up.full_name AS patient_name, ud.full_name AS doctor_name, d.specialty
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users up ON p.user_id = up.id
        LEFT JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN users ud ON d.user_id = ud.id
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_patient_dashboard_stats(patient_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM consultations WHERE patient_id = ?",
        (patient_id,)
    )
    total_consultations = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM consultations WHERE patient_id = ? AND status = 'pending'",
        (patient_id,)
    )
    pending_consultations = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM appointments WHERE patient_id = ? AND status = 'scheduled'",
        (patient_id,)
    )
    upcoming_appointments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
    total_doctors = cursor.fetchone()[0]

    conn.close()
    return {
        "total_consultations": total_consultations,
        "pending_consultations": pending_consultations,
        "upcoming_appointments": upcoming_appointments,
        "total_doctors": total_doctors,
    }


def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'patient'")
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
    total_doctors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM consultations WHERE status = 'pending'")
    pending_consultations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'scheduled'")
    upcoming_appointments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM consultations")
    total_consultations = cursor.fetchone()[0]

    conn.close()
    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "pending_consultations": pending_consultations,
        "upcoming_appointments": upcoming_appointments,
        "total_consultations": total_consultations,
    }
