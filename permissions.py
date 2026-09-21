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
