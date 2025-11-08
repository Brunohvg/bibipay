# apps/accounts/views.py

# ==========================
# IMPORTAÇÕES NECESSÁRIAS
# ==========================

# Views de autenticação padrão do Django
from django.contrib.auth.views import LoginView, LogoutView

# Views genéricas de CRUD (Create, Read, Update, Delete)
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView, View

# Funções úteis para manipular dados e redirecionar
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy

# Importa o modelo de usuário personalizado
from apps.accounts.models import User

# Importa formulários personalizados
from apps.accounts.forms import SellersCreationForm, SellersUpdateForm

# Função utilitária para redirecionar o usuário conforme o tipo
from apps.core.utils import redirect_user_by_type



# ==========================
# VIEW DE LOGIN PERSONALIZADA
# ==========================

class CustomLoginView(LoginView):
    """
    View de login customizada.
    Usa o template 'accounts/login.html' e redireciona o usuário
    de acordo com o tipo (admin, staff, seller etc).
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True  # Evita que usuários logados vejam a tela de login novamente

    def get_success_url(self):
        """
        Define para onde o usuário será redirecionado após o login.
        Usa uma função utilitária que verifica o tipo de usuário.
        """
        return redirect_user_by_type(self.request.user)

    def form_valid(self, form):
        """
        Executado quando o formulário de login é válido.
        Aqui, garantimos que a sessão expire ao fechar o navegador
        se o usuário não marcar 'lembrar-me'.
        """
        response = super().form_valid(form)

        # Se o usuário não marcou "lembrar-me", a sessão expira ao fechar o navegador.
        if not self.request.POST.get('remember_me'):
            self.request.session.set_expiry(0)
            self.request.session.modified = True

        return response

    def form_invalid(self, form):
        """
        Executado quando o formulário é inválido (login incorreto).
        Exibe uma mensagem de erro amigável ao usuário.
        """
        messages.error(self.request, "E-mail ou CPF e senha inválidos.", extra_tags='danger')
        return super().form_invalid(form)



# ==========================
# VIEW DE LOGOUT
# ==========================

class CustomLogoutView(LogoutView):
    """
    Faz o logout do usuário e redireciona para a página de login.
    """
    next_page = '/accounts/login/'



# ==========================
# CRIAÇÃO DE VENDEDORES
# ==========================

class SellersCreateView(CreateView):
    """
    View para cadastrar novos vendedores no sistema.
    """
    template_name = 'accounts/sellers_create.html'
    form_class = SellersCreationForm
    success_url = reverse_lazy('dashboard:admin')  # Boa prática: usar reverse_lazy em vez de string fixa

    def form_valid(self, form):
        """
        Exibe mensagem de sucesso quando o vendedor é criado.
        """
        messages.success(self.request, "Conta criada com sucesso! Faça login para continuar.", extra_tags='success')
        return super().form_valid(form)



# ==========================
# LISTAGEM DE VENDEDORES
# ==========================

class SellersListView(ListView):
    """
    Exibe uma lista de todos os vendedores cadastrados.
    """
    model = User
    template_name = 'accounts/sellers_list.html'
    context_object_name = 'sellers'

    def get_queryset(self):
        """
        Retorna apenas usuários do tipo 'sellers', ordenados por nome.
        """
        sellers = User.objects.filter(user_type='sellers').order_by('first_name', 'last_name')
        return sellers
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_sellers'] = self.get_queryset().filter(is_active=True)
        context['inactive_sellers'] = self.get_queryset().filter(is_active=False)
        return context


# ==========================
# DETALHES DE UM VENDEDOR
# ==========================

class SellersDetailView(DetailView):
    """
    Mostra os detalhes de um vendedor específico.
    """
    model = User
    template_name = 'accounts/sellers_detail.html'
    context_object_name = 'seller'

    def get_object(self, queryset=None):
        """
        Busca o vendedor pelo ID (pk) e garante que seja do tipo 'sellers'.
        """
        return get_object_or_404(User, pk=self.kwargs['pk'], user_type='sellers')



# ==========================
# ATUALIZAÇÃO DE VENDEDORES
# ==========================

class SellersUpdateView(UpdateView):
    """
    Permite editar os dados de um vendedor existente.
    """
    model = User
    form_class = SellersUpdateForm
    template_name = 'accounts/sellers_update.html'
    context_object_name = 'seller'
    success_url = reverse_lazy('accounts:sellers_list')

    def get_object(self, queryset=None):
        """
        Busca o vendedor e garante que seja do tipo 'sellers'.
        """
        return get_object_or_404(User, pk=self.kwargs['pk'], user_type='sellers')



# ==========================
# EXCLUSÃO DE VENDEDORES
# ==========================

class SellersDestroyView(DeleteView):
    """
    Permite excluir (deletar) um vendedor do sistema.
    """
    model = User
    template_name = 'accounts/sellers_confirm_delete.html'
    context_object_name = 'seller'
    success_url = reverse_lazy('accounts:sellers_list')

    def get_object(self, queryset=None):
        """
        Busca o vendedor e garante que seja do tipo 'sellers'.
        """
        return get_object_or_404(User, pk=self.kwargs['pk'], user_type='sellers')



# ==========================
# ATIVAR / DESATIVAR VENDEDOR
# ==========================

class SellersDeactivateView(View):
    """
    Ativa ou desativa um vendedor (sem excluir).
    Serve para bloquear o acesso de um vendedor sem perder os dados dele.
    """
    def get(self, request, pk, *args, **kwargs):
        # Busca o vendedor
        seller = get_object_or_404(User, pk=pk, user_type='sellers')

        # Alterna o status ativo/inativo
        seller.is_active = not seller.is_active
        seller.save()

        # Mensagem de sucesso dinâmica
        status = "ativado" if seller.is_active else "desativado"
        messages.success(request, f"Vendedor {status} com sucesso!", extra_tags='success')

        # Redireciona de volta para a lista de vendedores
        return redirect(reverse_lazy('accounts:sellers_list'))
