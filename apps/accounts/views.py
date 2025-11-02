from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from apps.core.utils import redirect_user_by_type

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return redirect_user_by_type(self.request.user)

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user:
            login(self.request, user)

            # Sessão expira ao fechar o navegador se não marcar "lembrar"
            if not self.request.POST.get('remember_me'):
                self.request.session.set_expiry(0)
                self.request.session.modified = True

            return super().form_valid(form)

        messages.error(self.request, "E-mail ou CPF e senha inválidos.", extra_tags='danger')
        return super().form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "E-mail ou CPF e senha inválidos.", extra_tags='danger')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = '/accounts/login/'
