from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_destino_pos_login(current_user))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario is None or not usuario.checar_senha(senha):
            flash("E-mail ou senha inválidos.", "error")
            return render_template("auth/login.html")

        if not usuario.ativo:
            flash("Este usuário está desativado. Fale com a administração.", "error")
            return render_template("auth/login.html")

        login_user(usuario)
        return redirect(_destino_pos_login(usuario))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))


def _destino_pos_login(usuario):
    if usuario.is_equipe:
        return url_for("admin.dashboard")
    return url_for("portal.dashboard")
