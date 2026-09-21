from flask import Blueprint, render_template
from flask_login import login_required, current_user

from permissions import responsavel_required

portal_bp = Blueprint("portal", __name__, url_prefix="/portal")


@portal_bp.route("/")
@login_required
@responsavel_required
def dashboard():
    meus_pacientes = current_user.pacientes_como_responsavel
    return render_template("portal/dashboard.html", pacientes=meus_pacientes)
