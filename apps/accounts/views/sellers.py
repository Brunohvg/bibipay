# apps/accounts/views.py
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView, View
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

# Importa o modelo e formulários (a view ainda precisa saber sobre eles)
from apps.accounts.models import User
from apps.accounts.forms import SellersCreationForm, SellersUpdateForm

# =========================================================
# MUDANÇA: Importamos nosso novo arquivo de serviços!
# =========================================================
from apps.accounts import services


# ==========================
# CRIAÇÃO DE VENDEDORES
# ==========================
class SellersCreateView(CreateView, LoginRequiredMixin):
    """
    (Sem mudança)
    Como explicado no 'services.py', esta view já separa bem a lógica.
    A view cuida do template/form/success_url, e o 'SellersCreationForm'
    (em forms.py) cuida da criação e validação do usuário.
    Está perfeito.
    """
    template_name = 'accounts/sellers/sellers_create.html'
    form_class = SellersCreationForm
    success_url = reverse_lazy('dashboard:dashboard_admin') 

    def form_valid(self, form):
        messages.success(self.request, "Conta criada com sucesso! Faça login para continuar.", extra_tags='success')
        return super().form_valid(form)


# ==========================
# LISTAGEM DE VENDEDORES
# ==========================
class SellersListView(ListView, LoginRequiredMixin):
    """
    Exibe uma lista de todos os vendedores cadastrados.
    A view agora pede a lista ao SERVIÇO.
    """
    model = User # Opcional, mas bom manter
    template_name = 'accounts/sellers/sellers_list.html'
    context_object_name = 'sellers'

    def get_queryset(self):
        """
        MUDANÇA: A view não sabe MAIS como buscar os vendedores.
        Ela simplesmente pede ao serviço.
        """
        return services.get_all_sellers()
    
    def get_context_data(self, **kwargs):
        """
        MUDANÇA: A lógica de separar ativos/inativos é da view
        (pois é para 'apresentação'), mas ela usa a lista
        principal vinda do serviço.
        """
        context = super().get_context_data(**kwargs)
        
        # Pega a lista principal (que já veio do get_queryset)
        all_sellers = context['sellers'] 
        
        # Filtra a lista para a exibição no template
        context['active_sellers'] = all_sellers.filter(is_active=True)
        context['inactive_sellers'] = all_sellers.filter(is_active=False)
        return context


# ==========================
# DETALHES DE UM VENDEDOR
# ==========================

class SellersDetailView(DetailView, LoginRequiredMixin):
    """
    Mostra os detalhes de um vendedor.
    A view pede o vendedor ao SERVIÇO.
    """
    model = User # Opcional
    template_name = 'accounts/sellers_detail.html'
    context_object_name = 'seller'

    def get_object(self, queryset=None):
        """
        MUDANÇA: A view não sabe MAIS como buscar o objeto.
        Ela pede ao serviço para buscar pelo ID.
        """
        return services.get_seller_by_id(user_id=self.kwargs['pk'])


# ==========================
# ATUALIZAÇÃO DE VENDEDORES
# ==========================
class SellersUpdateView(UpdateView, LoginRequiredMixin):
    """
    Permite editar os dados de um vendedor.
    A view pede o vendedor ao SERVIÇO.
    """
    model = User
    form_class = SellersUpdateForm
    template_name = 'accounts/sellers/sellers_update.html'
    context_object_name = 'seller'
    success_url = reverse_lazy('accounts:sellers_list')

    def get_object(self, queryset=None):
        """
        MUDANÇA: Reutilizamos o mesmo serviço!
        A lógica de 'get_object_or_404' está em um só lugar.
        """
        return services.get_seller_by_id(user_id=self.kwargs['pk'])


# ==========================
# EXCLUSÃO DE VENDEDORES
# ==========================
class SellersDestroyView(DeleteView, LoginRequiredMixin):
    """
    Permite excluir (deletar) um vendedor.
    A view pede o vendedor ao SERVIÇO.
    """
    model = User
    template_name = 'accounts/sellers_confirm_delete.html'
    context_object_name = 'seller'
    success_url = reverse_lazy('accounts:sellers_list')

    def get_object(self, queryset=None):
        """
        MUDANÇA: Reutilizamos o serviço mais uma vez.
        """
        return services.get_seller_by_id(user_id=self.kwargs['pk'])


# ==========================
# ATIVAR / DESATIVAR VENDEDOR
# ==========================
class SellersDeactivateView(View, LoginRequiredMixin):
    """
    Ativa ou desativa um vendedor (sem excluir).
    A view agora só CHAMA o serviço e exibe a mensagem.
    """
    def get(self, request, pk, *args, **kwargs):
        
        # ========================================================
        # MUDANÇA: A view não faz ideia de como o status é trocado.
        # Ela apenas pede para o serviço fazer a ação.
        # ========================================================
        try:
            seller = services.toggle_seller_status(user_id=pk)
            
            # A view continua responsável pelo Feedback ao usuário (HTTP)
            status = "ativado" if seller.is_active else "desativado"
            messages.success(request, f"Vendedor {status} com sucesso!", extra_tags='success')
        
        except Exception as e:
            # Se o serviço falhar (ex: não achar o usuário), a view trata o erro.
            messages.error(request, f"Erro ao atualizar vendedor: {e}", extra_tags='danger')

        # A view continua responsável pelo redirecionamento (HTTP)
        return redirect(reverse_lazy('accounts:sellers_list'))