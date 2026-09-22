from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import TarefaCasa
from permissions import equipe_required, responsavel_required, paciente_da_equipe_ou_403, paciente_do_responsavel_ou_403

# --- lado da equipe: cria e acompanha tarefas ---
tarefas_admin_bp = Blueprint(
    "tarefas_admin", __name__, url_prefix="/admin/pacientes/<int:paciente_id>/tarefas"
)


@tarefas_admin_bp.route("/")
@login_required
@equipe_required("admin", "terapeuta")
def listar(paciente_id):
    paciente = paciente_da_equipe_ou_403(paciente_id)
    lista = TarefaCasa.query.filter_by(paciente_id=paciente.id).order_by(TarefaCasa.criado_em.desc()).all()
    return render_template("admin/tarefas.html", paciente=paciente, tarefas=lista)


@tarefas_admin_bp.route("/nova", methods=["GET", "POST"])
@login_required
@equipe_required("admin", "terapeuta")
def nova(paciente_id):
    paciente = paciente_da_equipe_ou_403(paciente_id)

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip() or None
        prazo_str = request.form.get("prazo", "")

        if not titulo:
            flash("Informe um título pra tarefa.", "error")
            return render_template("admin/nova_tarefa.html", paciente=paciente)

        prazo = None
        if prazo_str:
            try:
                prazo = datetime.strptime(prazo_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Prazo inválido.", "error")
                return render_template("admin/nova_tarefa.html", paciente=paciente)

        tarefa = TarefaCasa(
            paciente_id=paciente.id,
            criado_por_id=current_user.id,
            titulo=titulo,
            descricao=descricao,
            prazo=prazo,
        )
        db.session.add(tarefa)
        db.session.commit()

        flash("Tarefa criada.", "success")
        return redirect(url_for("tarefas_admin.listar", paciente_id=paciente.id))

    return render_template("admin/nova_tarefa.html", paciente=paciente)


# --- lado do responsável: vê e marca como concluída ---
tarefas_portal_bp = Blueprint(
    "tarefas_portal", __name__, url_prefix="/portal/pacientes/<int:paciente_id>/tarefas"
)


@tarefas_portal_bp.route("/")
@login_required
@responsavel_required
def listar_portal(paciente_id):
    paciente = paciente_do_responsavel_ou_403(paciente_id)
    lista = TarefaCasa.query.filter_by(paciente_id=paciente.id).order_by(TarefaCasa.criado_em.desc()).all()
    return render_template("portal/tarefas.html", paciente=paciente, tarefas=lista)


@tarefas_portal_bp.route("/<int:tarefa_id>/concluir", methods=["POST"])
@login_required
@responsavel_required
def concluir(paciente_id, tarefa_id):
    paciente = paciente_do_responsavel_ou_403(paciente_id)
    tarefa = TarefaCasa.query.filter_by(id=tarefa_id, paciente_id=paciente.id).first_or_404()

    tarefa.concluida = True
    tarefa.concluida_em = datetime.utcnow()
    db.session.commit()

    flash("Tarefa marcada como concluída.", "success")
    return redirect(url_for("tarefas_portal.listar_portal", paciente_id=paciente.id))
