from datetime import datetime

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Agendamento
from permissions import responsavel_required

portal_bp = Blueprint("portal", __name__, url_prefix="/portal")


@portal_bp.route("/")
@login_required
@responsavel_required
def dashboard():
    meus_pacientes = current_user.pacientes_como_responsavel
    ids_pacientes = [p.id for p in meus_pacientes]

    proximos_agendamentos = []
    if ids_pacientes:
        proximos_agendamentos = (
            Agendamento.query.filter(
                Agendamento.paciente_id.in_(ids_pacientes),
                Agendamento.data_hora >= datetime.utcnow(),
                Agendamento.status == "agendado",
            )
            .order_by(Agendamento.data_hora)
            .all()
        )

    return render_template(
        "portal/dashboard.html", pacientes=meus_pacientes, agendamentos=proximos_agendamentos
    )
