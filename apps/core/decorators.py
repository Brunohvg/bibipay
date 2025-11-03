# apps/core/decorators.py
from functools import wraps
from django.shortcuts import redirect
from .utils import redirect_user_by_type
from functools import wraps
from django.shortcuts import redirect

def redirect_by_user_type(view_func):
    """
    Redireciona usuários logados para a tela correspondente ao tipo,
    evitando loop se já estiver na página correta.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            target_url = redirect_user_by_type(request.user)
            # Evita loop: só redireciona se o caminho atual for diferente
            if request.path != target_url:
                return redirect(target_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
