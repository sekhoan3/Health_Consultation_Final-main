from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from backend.auth import register_user, login_user
from backend.models import (
    get_patient_by_user_id,
    update_patient_profile,
    update_doctor_profile,
    get_doctor_by_user_id,
    get_all_doctors,
    create_consultation,
    get_consultations_by_patient,
    get_all_consultations,
    get_consultation_by_id,
    update_consultation_status,
    create_appointment,
    get_appointments_by_patient,
    get_all_appointments,
    update_appointment_status,
    get_dashboard_stats,
    get_patient_dashboard_stats,
)

bp = Blueprint("main", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated


@bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please fill in all fields.", "error")
            return render_template("auth/login.html")

        user, error = login_user(email, password)
        if error:
            flash(error, "error")
            return render_template("auth/login.html", email=email)

        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["user_role"] = user["role"]
        session["user_email"] = user["email"]
        flash(f"Welcome back, {user['full_name']}!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "patient")

        if not all([full_name, email, password, confirm_password]):
            flash("Please fill in all fields.", "error")
            return render_template("auth/register.html", full_name=full_name, email=email, role=role)

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html", full_name=full_name, email=email, role=role)

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("auth/register.html", full_name=full_name, email=email, role=role)

        user_id, error = register_user(full_name, email, password, role)
        if error:
            flash(error, "error")
            return render_template("auth/register.html", full_name=full_name, email=email, role=role)

        session["user_id"] = user_id
        session["user_name"] = full_name
        session["user_role"] = role
        session["user_email"] = email
        flash("Account created! Please complete your profile.", "success")
        return redirect(url_for("main.complete_profile"))

    return render_template("auth/register.html")


@bp.route("/register/profile", methods=["GET", "POST"])
@login_required
def complete_profile():
    user_id = session["user_id"]
    role = session["user_role"]

    if request.method == "POST":
        role = session["user_role"]

        if role == "doctor":
            specialty = request.form.get("specialty", "").strip()
            license_number = request.form.get("license_number", "").strip()
            phone = request.form.get("phone", "").strip()
            bio = request.form.get("bio", "").strip()

            if not specialty:
                flash("Specialty is required.", "error")
                return render_template("auth/complete_profile.html", role=role)
            if not license_number:
                flash("License number is required.", "error")
                return render_template("auth/complete_profile.html", role=role)
            if not phone:
                flash("Phone number is required.", "error")
                return render_template("auth/complete_profile.html", role=role)

            update_doctor_profile(user_id, {
                "specialty": specialty,
                "license_number": license_number,
                "phone": phone,
                "bio": bio,
            })

        else:
            data = {
                "date_of_birth": request.form.get("date_of_birth"),
                "gender": request.form.get("gender"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "blood_type": request.form.get("blood_type"),
                "allergies": request.form.get("allergies"),
                "emergency_contact": request.form.get("emergency_contact"),
                "emergency_phone": request.form.get("emergency_phone"),
            }
            update_patient_profile(user_id, data)

        flash("Profile completed successfully!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/complete_profile.html", role=role)


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    role = session["user_role"]
    stats = get_dashboard_stats()

    if role == "patient":
        patient = get_patient_by_user_id(user_id)
        if patient:
            consultations = get_consultations_by_patient(patient["id"])[:5]
            appointments = get_appointments_by_patient(patient["id"])[:5]
            stats = get_patient_dashboard_stats(patient["id"])
        else:
            consultations, appointments = [], []
            stats = {"total_consultations": 0, "pending_consultations": 0, "upcoming_appointments": 0, "total_doctors": 0}
        return render_template("dashboard/patient_dashboard.html",
                               stats=stats, consultations=consultations,
                               appointments=appointments, patient=patient)

    elif role == "doctor":
        doctor = get_doctor_by_user_id(user_id)
        consultations = get_all_consultations()[:5]
        appointments = get_all_appointments()[:5]
        return render_template("dashboard/doctor_dashboard.html",
                               stats=stats, consultations=consultations,
                               appointments=appointments, doctor=doctor)

    return redirect(url_for("admin.dashboard"))


@bp.route("/consultations")
@login_required
def consultations():
    user_id = session["user_id"]
    role = session["user_role"]

    if role == "patient":
        patient = get_patient_by_user_id(user_id)
        items = get_consultations_by_patient(patient["id"]) if patient else []
    else:
        items = get_all_consultations()

    return render_template("consultations/list.html", consultations=items, role=role)


@bp.route("/consultations/new", methods=["GET", "POST"])
@login_required
def new_consultation():
    user_id = session["user_id"]

    if request.method == "POST":
        patient = get_patient_by_user_id(user_id)
        if not patient:
            flash("Patient profile not found.", "error")
            return redirect(url_for("main.dashboard"))

        data = {
            "chief_complaint": request.form.get("chief_complaint"),
            "symptoms": request.form.get("symptoms"),
            "duration": request.form.get("duration"),
            "severity": request.form.get("severity"),
            "medical_history": request.form.get("medical_history"),
            "current_medications": request.form.get("current_medications"),
            "notes": request.form.get("notes"),
        }
        create_consultation(patient["id"], data)
        flash("Consultation request submitted successfully.", "success")
        return redirect(url_for("main.consultations"))

    return render_template("consultations/new.html")


@bp.route("/consultations/<int:consultation_id>")
@login_required
def view_consultation(consultation_id):
    consultation = get_consultation_by_id(consultation_id)
    if not consultation:
        flash("Consultation not found.", "error")
        return redirect(url_for("main.consultations"))
    return render_template("consultations/view.html", consultation=consultation)


@bp.route("/consultations/<int:consultation_id>/update", methods=["POST"])
@login_required
def update_consultation(consultation_id):
    if session["user_role"] not in ("doctor", "admin"):
        flash("Permission denied.", "error")
        return redirect(url_for("main.consultations"))

    status = request.form.get("status")
    notes = request.form.get("notes")
    update_consultation_status(consultation_id, status, notes)
    flash("Consultation updated.", "success")
    return redirect(url_for("main.view_consultation", consultation_id=consultation_id))


@bp.route("/appointments")
@login_required
def appointments():
    user_id = session["user_id"]
    role = session["user_role"]

    if role == "patient":
        patient = get_patient_by_user_id(user_id)
        items = get_appointments_by_patient(patient["id"]) if patient else []
    else:
        items = get_all_appointments()

    return render_template("appointments/list.html", appointments=items, role=role)


@bp.route("/appointments/new", methods=["GET", "POST"])
@login_required
def new_appointment():
    user_id = session["user_id"]
    doctors = get_all_doctors()

    if request.method == "POST":
        patient = get_patient_by_user_id(user_id)
        if not patient:
            flash("Patient profile not found.", "error")
            return redirect(url_for("main.dashboard"))

        data = {
            "doctor_id": request.form.get("doctor_id"),
            "appointment_date": request.form.get("appointment_date"),
            "appointment_time": request.form.get("appointment_time"),
            "type": request.form.get("type", "in-person"),
            "notes": request.form.get("notes"),
        }
        create_appointment(patient["id"], data)
        flash("Appointment booked successfully.", "success")
        return redirect(url_for("main.appointments"))

    return render_template("appointments/new.html", doctors=doctors)


@bp.route("/appointments/<int:appointment_id>/update", methods=["POST"])
@login_required
def update_appointment(appointment_id):
    if session["user_role"] not in ("doctor", "admin"):
        flash("Permission denied.", "error")
        return redirect(url_for("main.appointments"))

    status = request.form.get("status")
    allowed = {"scheduled", "completed", "cancelled"}
    if status not in allowed:
        flash("Invalid status value.", "error")
        return redirect(url_for("main.appointments"))

    update_appointment_status(appointment_id, status)
    flash("Appointment status updated.", "success")
    return redirect(url_for("main.appointments"))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    role = session["user_role"]

    if role == "patient":
        profile_data = get_patient_by_user_id(user_id)
    else:
        profile_data = get_doctor_by_user_id(user_id)

    if request.method == "POST" and role == "patient":
        data = {
            "date_of_birth": request.form.get("date_of_birth"),
            "gender": request.form.get("gender"),
            "phone": request.form.get("phone"),
            "address": request.form.get("address"),
            "blood_type": request.form.get("blood_type"),
            "allergies": request.form.get("allergies"),
            "emergency_contact": request.form.get("emergency_contact"),
            "emergency_phone": request.form.get("emergency_phone"),
        }
        update_patient_profile(user_id, data)
        flash("Profile updated successfully.", "success")
        return redirect(url_for("main.profile"))

    return render_template("profile/index.html", profile=profile_data, role=role)
