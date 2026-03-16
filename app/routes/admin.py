from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.models.settings import SystemSettings
from app.models.holiday import Holiday
from app.extensions import db
from datetime import datetime


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@login_required
def dashboard():
    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    return render_template("admin/dashboard.html")

@admin_bp.route("/settings/general", methods=["GET", "POST"])
@login_required
def settings_general():

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    settings = SystemSettings.query.first()

    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()

    if request.method == "POST":

        form_type = request.form.get("form_type")

        # GENERAL SETTINGS FORM
        if form_type == "general":
            settings.system_name = request.form["system_name"]
            settings.timezone = request.form["timezone"]

            db.session.commit()
            flash("Settings updated")

        # ADD HOLIDAY FORM
        elif form_type == "holiday":
            holiday = Holiday(
                date=datetime.strptime(request.form["date"], "%Y-%m-%d"),
                name=request.form["name"],
                type=request.form["type"],
                description=request.form["description"]
            )

            db.session.add(holiday)
            db.session.commit()

            flash("Holiday added")

        return redirect(url_for("admin.settings_general"))

    holidays = Holiday.query.order_by(Holiday.date.asc()).all()

    return render_template(
        "admin/settings/general.html",
        settings=settings,
        holidays=holidays
    )

@admin_bp.route("/settings/holidays/delete/<int:id>", methods=["POST"])
@login_required
def delete_holiday(id):

    holiday = Holiday.query.get_or_404(id)

    db.session.delete(holiday)
    db.session.commit()

    flash("Holiday deleted")

    return redirect(url_for("admin.settings_general"))

@admin_bp.route("/users")
@login_required
def users():

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    users = User.query.all()

    return render_template("admin/user.html", users=users)

@admin_bp.route("/users/create", methods=["POST"])
@login_required
def create_user():

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    user = User(username=username, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    flash("User created successfully")

    return redirect(url_for("admin.users"))

@admin_bp.route("/users/reset/<int:id>", methods=["POST"])
@login_required
def reset_password(id):

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    user = User.query.get_or_404(id)

    new_password = request.form["password"]

    user.set_password(new_password)

    db.session.commit()

    flash("Password reset successfully")

    return redirect(url_for("admin.users"))

@admin_bp.route("/users/delete/<int:id>", methods=["POST"])
@login_required
def delete_user(id):

    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("secretary.dashboard"))

    user = User.query.get_or_404(id)

    if user.role == "superadmin":
        flash("Superadmin cannot be deleted.")
        return redirect(url_for("admin.users"))

    if user.id == current_user.id:
        flash("You cannot delete your own account.")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted")

    return redirect(url_for("admin.users"))