from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Agendamento, Paciente, Usuario, STATUS_AGENDAMENTO
from permissions import equipe_required

agendamentos_bp = Blueprint("agendamentos", __name__, url_prefix="/admin/agendamentos")


@agendamentos_bp.route("/")
@login_required
@equipe_required()
def listar():
    query = Agendamento.query.order_by(Agendamento.data_hora)

    if current_user.papel == "terapeuta":
        query = query.filter_by(terapeuta_id=current_user.id)

    lista = query.all()
    return render_template("admin/agendamentos.html", agendamentos=lista)


@agendamentos_bp.route("/novo", methods=["GET", "POST"])
@login_required
@equipe_required("admin", "secretaria", "terapeuta")
def novo():
    pacientes = Paciente.query.filter_by(ativo=True).order_by(Paciente.nome).all()

    if current_user.papel == "terapeuta":
        # terapeuta só agenda pra pacientes dele
        pacientes = [p for p in pacientes if p.terapeuta_id == current_user.id]
        terapeutas = [current_user]
    else:
        terapeutas = Usuario.query.filter_by(tipo="equipe", papel="terapeuta", ativo=True).order_by(Usuario.nome).all()

    if request.method == "POST":
        paciente_id = request.form.get("paciente_id")
        terapeuta_id = request.form.get("terapeuta_id")
        data_str = request.form.get("data")
        hora_str = request.form.get("hora")
        duracao = request.form.get("duracao_minutos", "50")
        observacao = request.form.get("observacao", "").strip() or None

        if not paciente_id or not terapeuta_id or not data_str or not hora_str:
            flash("Preencha paciente, terapeuta, data e horário.", "error")
            return render_template("admin/novo_agendamento.html", pacientes=pacientes, terapeutas=terapeutas)

        try:
            data_hora = datetime.strptime(f"{data_str} {hora_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash("Data ou horário inválido.", "error")
            return render_template("admin/novo_agendamento.html", pacientes=pacientes, terapeutas=terapeutas)

        # terapeuta só pode marcar pra ele mesmo, mesmo que tente forçar outro id
        if current_user.papel == "terapeuta":
            terapeuta_id = current_user.id

        agendamento = Agendamento(
            paciente_id=int(paciente_id),
            terapeuta_id=int(terapeuta_id),
            data_hora=data_hora,
            duracao_minutos=int(duracao),
            observacao=observacao,
        )
        db.session.add(agendamento)
        db.session.commit()

        flash("Agendamento criado com sucesso.", "success")
        return redirect(url_for("agendamentos.listar"))

    return render_template("admin/novo_agendamento.html", pacientes=pacientes, terapeutas=terapeutas)


@agendamentos_bp.route("/<int:agendamento_id>/status", methods=["POST"])
@login_required
@equipe_required()
def mudar_status(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)

    # terapeuta só mexe nos agendamentos dele
    if current_user.papel == "terapeuta" and agendamento.terapeuta_id != current_user.id:
        flash("Você não tem permissão para alterar esse agendamento.", "error")
        return redirect(url_for("agendamentos.listar"))

    novo_status = request.form.get("status")
    if novo_status not in STATUS_AGENDAMENTO:
        flash("Status inválido.", "error")
        return redirect(url_for("agendamentos.listar"))

    agendamento.status = novo_status
    db.session.commit()
    flash("Status atualizado.", "success")
    return redirect(url_for("agendamentos.listar"))
