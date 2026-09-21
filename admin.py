from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Usuario, Paciente, PAPEIS_EQUIPE
from permissions import equipe_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@equipe_required()
def dashboard():
    total_pacientes = Paciente.query.filter_by(ativo=True).count()
    total_usuarios = Usuario.query.filter_by(ativo=True).count()
    return render_template(
        "admin/dashboard.html",
        total_pacientes=total_pacientes,
        total_usuarios=total_usuarios,
    )


@admin_bp.route("/pacientes")
@login_required
@equipe_required()
def pacientes():
    if current_user.papel == "terapeuta":
        lista = Paciente.query.filter_by(terapeuta_id=current_user.id, ativo=True).all()
    else:
        lista = Paciente.query.filter_by(ativo=True).all()
    return render_template("admin/pacientes.html", pacientes=lista)


@admin_bp.route("/usuarios")
@login_required
@equipe_required("admin")
def usuarios():
    lista = Usuario.query.order_by(Usuario.tipo, Usuario.nome).all()
    return render_template("admin/usuarios.html", usuarios=lista)


@admin_bp.route("/usuarios/novo", methods=["GET", "POST"])
@login_required
@equipe_required("admin")
def novo_usuario():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        tipo = request.form.get("tipo")
        papel = request.form.get("papel") or None

        if not nome or not email or not senha:
            flash("Preencha nome, e-mail e senha.", "error")
            return render_template("admin/novo_usuario.html", papeis=PAPEIS_EQUIPE)

        if Usuario.query.filter_by(email=email).first():
            flash("Já existe um usuário com esse e-mail.", "error")
            return render_template("admin/novo_usuario.html", papeis=PAPEIS_EQUIPE)

        if tipo == "equipe" and papel not in PAPEIS_EQUIPE:
            flash("Selecione um papel válido para a equipe.", "error")
            return render_template("admin/novo_usuario.html", papeis=PAPEIS_EQUIPE)

        novo = Usuario(
            nome=nome,
            email=email,
            tipo=tipo,
            papel=papel if tipo == "equipe" else None,
        )
        novo.set_senha(senha)
        db.session.add(novo)
        db.session.commit()

        flash(f"Usuário {nome} criado com sucesso.", "success")
        return redirect(url_for("admin.usuarios"))

    return render_template("admin/novo_usuario.html", papeis=PAPEIS_EQUIPE)
