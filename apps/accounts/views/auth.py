# apps/accounts/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.contrib import messages

# Utils (perfeito, continua como está)
from apps.core.utils import redirect_user_by_type
# =========================================================


# ==========================
# VIEW DE LOGIN PERSONALIZADA
# ==========================
class CustomLoginView(LoginView):
    """
    (Sem mudança)
    Esta view já está ótima. A lógica de "redirecionar" (utils) e
    "lembrar-me" (sessão) é responsabilidade da view (HTTP),
    e não do negócio.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True 

    def get_success_url(self):
        return redirect_user_by_type(self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.request.POST.get('remember_me'):
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return response

    def form_invalid(self, form):
        messages.error(self.request, "E-mail ou CPF e senha inválidos.", extra_tags='danger')
        return super().form_invalid(form)


# ==========================
# VIEW DE LOGOUT
# ==========================
class CustomLogoutView(LogoutView):
    """(Sem mudança)"""
    next_page = '/accounts/login/'
