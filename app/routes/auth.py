from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.extensions import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # check current password
        if not current_user.check_password(current_password):
            flash("Current password is incorrect")
            return redirect(url_for("auth.change_password"))

        # check new password match
        if new_password != confirm_password:
            flash("New passwords do not match")
            return redirect(url_for("auth.change_password"))

        # update password
        current_user.set_password(new_password)

        db.session.commit()

        flash("Password updated successfully")
        return redirect(url_for("secretary.dashboard"))

    return render_template("auth/change_password.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)

            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user.role == "secretary":
                return redirect(url_for("secretary.dashboard"))

        flash("Invalid username or password")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))