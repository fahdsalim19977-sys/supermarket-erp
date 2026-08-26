from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db.session.scalar(db.select(User).where(User.username == username))

        if not user or not user.is_active or not user.check_password(password):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html"), 401

        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        login_user(user)
        return redirect(request.args.get("next") or url_for("main.dashboard"))

    return render_template("auth/login.html")


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
