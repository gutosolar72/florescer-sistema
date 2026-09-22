from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Mensagem
from permissions import equipe_required, responsavel_required, paciente_da_equipe_ou_403, paciente_do_responsavel_ou_403

# --- lado da equipe ---
comunicacao_admin_bp = Blueprint(
    "comunicacao_admin", __name__, url_prefix="/admin/pacientes/<int:paciente_id>/comunicacao"
)


@comunicacao_admin_bp.route("/", methods=["GET", "POST"])
@login_required
@equipe_required("admin", "terapeuta")
def conversa(paciente_id):
    paciente = paciente_da_equipe_ou_403(paciente_id)

    if request.method == "POST":
        texto = request.form.get("texto", "").strip()
        if texto:
            db.session.add(Mensagem(paciente_id=paciente.id, autor_id=current_user.id, texto=texto))
            db.session.commit()
        return redirect(url_for("comunicacao_admin.conversa", paciente_id=paciente.id))

    mensagens = Mensagem.query.filter_by(paciente_id=paciente.id).order_by(Mensagem.criado_em).all()
    return render_template("admin/comunicacao.html", paciente=paciente, mensagens=mensagens)


# --- lado do responsável ---
comunicacao_portal_bp = Blueprint(
    "comunicacao_portal", __name__, url_prefix="/portal/pacientes/<int:paciente_id>/comunicacao"
)


@comunicacao_portal_bp.route("/", methods=["GET", "POST"])
@login_required
@responsavel_required
def conversa_portal(paciente_id):
    paciente = paciente_do_responsavel_ou_403(paciente_id)

    if request.method == "POST":
        texto = request.form.get("texto", "").strip()
        if texto:
            db.session.add(Mensagem(paciente_id=paciente.id, autor_id=current_user.id, texto=texto))
            db.session.commit()
        return redirect(url_for("comunicacao_portal.conversa_portal", paciente_id=paciente.id))

    mensagens = Mensagem.query.filter_by(paciente_id=paciente.id).order_by(Mensagem.criado_em).all()
    return render_template("portal/comunicacao.html", paciente=paciente, mensagens=mensagens)
