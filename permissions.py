from functools import wraps

from flask import abort
from flask_login import current_user


def equipe_required(*papeis):
    """Libera a rota só para usuários da equipe (tipo='equipe').
    Se `papeis` for passado, restringe também pelo papel específico.
    Ex: @equipe_required() -> qualquer um da equipe
        @equipe_required('admin') -> só admin
        @equipe_required('admin', 'terapeuta') -> admin ou terapeuta
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_equipe:
                abort(403)
            if papeis and current_user.papel not in papeis:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def responsavel_required(view_func):
    """Libera a rota só para responsáveis (tipo='responsavel')."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_responsavel:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


def paciente_do_responsavel_ou_403(paciente_id):
    """Garante que o paciente pedido é vinculado ao responsável logado.
    Retorna o Paciente se estiver tudo certo, senão aborta com 403."""
    from models import Paciente

    paciente = Paciente.query.get_or_404(paciente_id)
    if paciente not in current_user.pacientes_como_responsavel:
        abort(403)
    return paciente


def paciente_da_equipe_ou_403(paciente_id):
    """Garante que, se o usuário logado é terapeuta, o paciente pedido é
    atribuído a ele. Admin/secretaria passam livre. Retorna o Paciente."""
    from models import Paciente

    paciente = Paciente.query.get_or_404(paciente_id)
    if current_user.papel == "terapeuta" and paciente.terapeuta_id != current_user.id:
        abort(403)
    return paciente
