from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm
from .models import User

bp = Blueprint("auth", __name__, template_folder="templates")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # если админ — в админку, если нет — на главную
        if current_user.is_admin:
            return redirect(url_for("main.admin_categories"))
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Добро пожаловать, {user.username}!", "success")

            # куда редиректить после входа
            if user.is_admin:
                next_page = request.args.get("next") or url_for("main.index")
            else:
                next_page = request.args.get("next") or url_for("main.index")

            return redirect(next_page)

        flash("Неверное имя пользователя или пароль.", "danger")

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("main.index"))
