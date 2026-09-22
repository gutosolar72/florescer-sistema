from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import Paciente, Evolucao, Agendamento
from permissions import equipe_required

evolucoes_bp = Blueprint("evolucoes", __name__, url_prefix="/admin/pacientes/<int:paciente_id>/evolucoes")


def _paciente_ou_403(paciente_id):
    """Busca o paciente e garante que o terapeuta só acesse os próprios."""
    paciente = Paciente.query.get_or_404(paciente_id)
    if current_user.papel == "terapeuta" and paciente.terapeuta_id != current_user.id:
        abort(403)
    return paciente


@evolucoes_bp.route("/")
@login_required
@equipe_required("admin", "terapeuta")
def listar(paciente_id):
    paciente = _paciente_ou_403(paciente_id)
    lista = Evolucao.query.filter_by(paciente_id=paciente.id).order_by(Evolucao.data.desc()).all()
    return render_template("admin/evolucoes.html", paciente=paciente, evolucoes=lista)


@evolucoes_bp.route("/nova", methods=["GET", "POST"])
@login_required
@equipe_required("admin", "terapeuta")
def nova(paciente_id):
    paciente = _paciente_ou_403(paciente_id)

    # agendamentos recentes desse paciente, pra vincular a evolução (opcional)
    agendamentos = (
        Agendamento.query.filter_by(paciente_id=paciente.id)
        .order_by(Agendamento.data_hora.desc())
        .limit(10)
        .all()
    )

    if request.method == "POST":
        data_str = request.form.get("data", "")
        texto = request.form.get("texto", "").strip()
        agendamento_id = request.form.get("agendamento_id") or None

        if not texto:
            flash("Escreva o conteúdo da evolução.", "error")
            return render_template(
                "admin/nova_evolucao.html", paciente=paciente, agendamentos=agendamentos
            )

        try:
            data_evolucao = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else date.today()
        except ValueError:
            flash("Data inválida.", "error")
            return render_template(
                "admin/nova_evolucao.html", paciente=paciente, agendamentos=agendamentos
            )

        evolucao = Evolucao(
            paciente_id=paciente.id,
            terapeuta_id=current_user.id,
            agendamento_id=int(agendamento_id) if agendamento_id else None,
            data=data_evolucao,
            texto=texto,
        )
        db.session.add(evolucao)
        db.session.commit()

        flash("Evolução registrada.", "success")
        return redirect(url_for("evolucoes.listar", paciente_id=paciente.id))

    return render_template("admin/nova_evolucao.html", paciente=paciente, agendamentos=agendamentos)
