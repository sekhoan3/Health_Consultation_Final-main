from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.admin_models import (
    get_all_users, get_user_by_id, update_user_role, delete_user,
    create_user_by_admin, get_admin_stats, assign_doctor_to_consultation,
    update_appointment_status, get_all_doctors_simple,
)
from backend.models import (
    get_all_consultations, get_consultation_by_id, update_consultation_status,
    get_all_appointments,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in.", "warning")
            return redirect(url_for("main.login"))
        if session.get("user_role") != "admin":
            flash("Access denied. Admin only.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = get_admin_stats()
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/users")
@admin_required
def users():
    all_users = get_all_users()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@admin_required
def create_user():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email     = request.form.get("email", "").strip()
        password  = request.form.get("password", "")
        role      = request.form.get("role", "patient")

        if not all([full_name, email, password]):
            flash("All fields are required.", "error")
            return render_template("admin/user_form.html", action="create")

        user_id, error = create_user_by_admin(full_name, email, password, role)
        if error:
            flash(error, "error")
            return render_template("admin/user_form.html", action="create",
                                   full_name=full_name, email=email, role=role)
        flash(f"User '{full_name}' created successfully.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_form.html", action="create")


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.users"))

    if request.method == "POST":
        new_role = request.form.get("role")
        if new_role not in ("patient", "doctor", "admin"):
            flash("Invalid role.", "error")
            return render_template("admin/user_form.html", action="edit", user=user)
        update_user_role(user_id, new_role)
        flash(f"Role updated to '{new_role}'.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_form.html", action="edit", user=user)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user_route(user_id):
    if user_id == session["user_id"]:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("admin.users"))
    user = get_user_by_id(user_id)
    if user:
        delete_user(user_id)
        flash(f"User '{user['full_name']}' deleted.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/consultations")
@admin_required
def consultations():
    items = get_all_consultations()
    doctors = get_all_doctors_simple()
    return render_template("admin/consultations.html", consultations=items, doctors=doctors)


@admin_bp.route("/consultations/<int:cid>/assign", methods=["POST"])
@admin_required
def assign_doctor(cid):
    doctor_id = request.form.get("doctor_id")
    if doctor_id:
        assign_doctor_to_consultation(cid, int(doctor_id))
        flash("Doctor assigned successfully.", "success")
    return redirect(url_for("admin.consultations"))


@admin_bp.route("/consultations/<int:cid>/update", methods=["POST"])
@admin_required
def update_consultation(cid):
    status = request.form.get("status")
    notes  = request.form.get("notes", "")
    update_consultation_status(cid, status, notes)
    flash("Consultation updated.", "success")
    return redirect(url_for("admin.consultations"))


@admin_bp.route("/appointments")
@admin_required
def appointments():
    items = get_all_appointments()
    return render_template("admin/appointments.html", appointments=items)


@admin_bp.route("/appointments/<int:aid>/update", methods=["POST"])
@admin_required
def update_appointment(aid):
    status = request.form.get("status")
    update_appointment_status(aid, status)
    flash("Appointment status updated.", "success")
    return redirect(url_for("admin.appointments"))
