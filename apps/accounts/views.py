from django.contrib.auth.views import LoginView
from django.contrib import messages

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    # form_class = LoginForm # Se estiver usando a classe de formulário customizada

    def form_valid(self, form):
        """Se o formulário for válido, configura a sessão e loga o usuário."""
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        
        # A chamada para super().form_valid(form) executa o login
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Se o formulário for inválido (login falhou), 
        captura a mensagem de erro e a envia via messages framework.
        """
        # A mensagem de erro padrão está na chave '__all__' ou 'username'
        error_message = 'E-mail ou senha inválidos. Por favor, tente novamente.'
        
        # Tenta pegar erros não-campo (que são erros de autenticação, como credenciais incorretas)
        if form.non_field_errors():
            error_message = form.non_field_errors().as_text()
            print("Non-field errors:", error_message)
        
        # Ou, para simplificar e focar na credencial, usa a mensagem genérica:
        messages.error(self.request, error_message, extra_tags='danger')
        
        # Retorna para o template para exibir a mensagem.
        return super().form_invalid(form)

class CustomResetPasswordView():
    pass


class CustomResetPasswordConfirmView():
    pass


class CustomChangePasswordView():
    pass

