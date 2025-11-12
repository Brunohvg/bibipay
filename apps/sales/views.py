# apps/sales/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, ListView, DeleteView, UpdateView # 👈 Adicione UpdateView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from decimal import Decimal
import datetime

from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import Sale
from .forms import SaleForm
from .services import create_sale, get_sales_by_seller 

# ==================================
# CREATE VIEW (Sem mudanças)
# ==================================
class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sales_create.html'
    success_url = reverse_lazy('sales:sales_list')
    login_url = 'accounts:login'

    def form_valid(self, form):
        try:
            self.object = create_sale(self.request.user, form)
            messages.success(self.request, "Venda criada com sucesso!", extra_tags='success')
            return redirect(self.get_success_url())
            
        except ValidationError as e:
            error_message = e.messages[0] if hasattr(e, 'messages') else str(e)
            messages.error(
                self.request, 
                error_message, 
                extra_tags='danger'
            )
            return self.form_invalid(form)

# ==================================
# LIST VIEW (Filtro por Dia Adicionado)
# ==================================
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
        
        queryset = get_sales_by_seller(user.id) # Pega todas

        # Lógica de Filtro
        if 'year' in self.request.GET or 'month' in self.request.GET or 'day' in self.request.GET:
            self.selected_year = self.request.GET.get('year', '')
            self.selected_month = self.request.GET.get('month', '')
            self.selected_day = self.request.GET.get('day', '')
        else:
            # Padrão: Mês e Ano atuais
            today = datetime.date.today()
            self.selected_year = str(today.year)
            self.selected_month = str(today.month)
            self.selected_day = '' # Não filtramos o dia por padrão

        # Aplica filtros
        if self.selected_year:
            queryset = queryset.filter(date__year=self.selected_year)
        if self.selected_month:
            queryset = queryset.filter(date__month=self.selected_month)
        if self.selected_day:
            queryset = queryset.filter(date__day=self.selected_day)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        commission_rate = getattr(user, 'commission_rate', Decimal('0.00'))
        
        # 1. CALCULA TOTAIS DO FILTRO
        totals = self.object_list.aggregate(
            total_vendas=Coalesce(Sum('total_amount'), Decimal('0.00'))
        )
        total_sales_amount = totals['total_vendas']
        total_commission_amount = (total_sales_amount * commission_rate) / Decimal('100')

        context['total_sales_filtered'] = f"{total_sales_amount:.2f}".replace(".", ",")
        context['total_commission_filtered'] = f"{total_commission_amount:.2f}".replace(".", ",")

        # 2. Calcula comissão para os itens da PÁGINA ATUAL
        sales_list = context.get('sales', [])
        sales_with_commission = []
        for sale in sales_list:
            sale.calculated_commission = (sale.total_amount * commission_rate) / Decimal('100')
            sales_with_commission.append(sale)
        
        context['sales'] = sales_with_commission
        
        # 3. Envia dados dos filtros para o template
        context['selected_year'] = self.selected_year
        context['selected_month'] = self.selected_month
        context['selected_day'] = self.selected_day # 👈 Novo
        
        context['month_choices'] = [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
            (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
            (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
        ]
        current_year = datetime.date.today().year
        context['year_choices'] = [str(y) for y in range(current_year, current_year - 5, -1)]
        context['day_choices'] = [str(d) for d in range(1, 32)] # 👈 Novo
        
        return context

# ==================================
# NOVA VIEW DE DELEÇÃO
# ==================================
class SaleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sales:sales_list')
    context_object_name = 'sale'

    def get_queryset(self):
        """
        Garante que o usuário logado SÓ POSSA deletar as 
        próprias vendas.
        """
        queryset = super().get_queryset()
        return queryset.filter(seller=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Venda excluída com sucesso.", extra_tags='success')
        return super().form_valid(form)
    
# ==================================
# NOVA VIEW DE ATUALIZAÇÃO (EDIÇÃO)
# ==================================
class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm # Reutiliza o mesmo formulário da criação
    template_name = 'sales/sale_update.html'
    success_url = reverse_lazy('sales:sales_list')
    login_url = 'accounts:login'
    context_object_name = 'sale'

    def get_queryset(self):
        """
        Segurança: Garante que o usuário logado SÓ POSSA editar as 
        próprias vendas.
        """
        queryset = super().get_queryset()
        return queryset.filter(seller=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Venda atualizada com sucesso.", extra_tags='success')
        return super().form_valid(form)