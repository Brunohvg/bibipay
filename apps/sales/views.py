# apps/sales/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError

from .models import Sale
from .forms import SaleForm
# Importa os serviços atualizados e mais inteligentes
from .services import create_sale, get_sales_by_seller, get_sales_dashboard_stats 

class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sales_create.html'
    success_url = reverse_lazy('sales:sales_list') # ← Mudei para a lista
    login_url = 'accounts:login'

    def form_valid(self, form):
        try:
            self.object = create_sale(self.request.user, form)
            messages.success(self.request, "Venda criada com sucesso!", extra_tags='success')
            return redirect(self.get_success_url())
        except ValidationError as e:
            error_message = e.messages[0] if hasattr(e, 'messages') else str(e)
            messages.error(self.request, error_message, extra_tags='danger')
            return self.form_invalid(form)
            
        except ValidationError as e:
            # Se o serviço falhar (ex: duplicado), ele avisa
            error_message = e.messages[0] if hasattr(e, 'messages') else str(e)
            messages.error(
                self.request, 
                error_message, 
                extra_tags='danger'
            )
            return self.form_invalid(form)


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    login_url = 'accounts:login'

    def get_queryset(self):
        user = self.request.user
        
        if getattr(user, 'user_type', None) != 'sellers':
            return Sale.objects.none()
        
        # ======= A VIEW SÓ PASSA OS PARÂMETROS =======
        period = self.request.GET.get('period')
        
        # A view não sabe MAIS como filtrar, ela só pede ao serviço.
        return get_sales_by_seller(user.id, period=period)
    
    def get_context_data(self, **kwargs):
        # A lógica de estatística foi movida.
        # Você pode criar um serviço 'get_list_stats' se precisar,
        # ou manter agregações simples aqui (Sum, Count) do queryset.
        context = super().get_context_data(**kwargs)
        context['stats'] = get_sales_dashboard_stats(self.request.user.id)
        return context
