# apps/sales/views.py
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from decimal import Decimal
import datetime

from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import Sale
from .forms import SaleForm
from .services import create_sale, get_sales_by_seller
from apps.commissions.models import Commission  # 👈 Import correto

# ============================================================
# CREATE VIEW
# ============================================================
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
            messages.error(self.request, error_message, extra_tags='danger')
            return self.form_invalid(form)


# ============================================================
# LIST VIEW (com correção de comissão e filtros)
# ============================================================
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

        queryset = get_sales_by_seller(user.id)

        # Lógica de filtro
        if any(k in self.request.GET for k in ['year', 'month', 'day']):
            self.selected_year = self.request.GET.get('year', '')
            self.selected_month = self.request.GET.get('month', '')
            self.selected_day = self.request.GET.get('day', '')
        else:
            today = datetime.date.today()
            self.selected_year = str(today.year)
            self.selected_month = str(today.month)
            self.selected_day = ''

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

        # Comissão padrão do usuário (fallback, se necessário)
        commission_rate = getattr(user, 'commission_rate', Decimal('0.00'))

        # 1️⃣ Totais gerais filtrados
        totals = self.object_list.aggregate(
            total_vendas=Coalesce(Sum('total_amount'), Decimal('0.00'))
        )
        total_sales_amount = totals['total_vendas']

        # Somar comissões REAIS do banco (não recalculadas)
        total_commission_amount = Commission.objects.filter(
            sale__in=self.object_list
        ).aggregate(
            total_comissoes=Coalesce(Sum('value'), Decimal('0.00'))
        )['total_comissoes']

        context['total_sales_filtered'] = f"{total_sales_amount:.2f}".replace(".", ",")
        context['total_commission_filtered'] = f"{total_commission_amount:.2f}".replace(".", ",")

        # 2️⃣ Atribuir comissão real de cada venda
        sales_list = context.get('sales', [])
        sales_with_commission = []

        for sale in sales_list:
            commission = Commission.objects.filter(sale=sale).first()
            sale.calculated_commission = commission.value if commission else Decimal('0.00')
            sales_with_commission.append(sale)

        context['sales'] = sales_with_commission

        # 3️⃣ Filtros disponíveis
        context['selected_year'] = self.selected_year
        context['selected_month'] = self.selected_month
        context['selected_day'] = self.selected_day

        context['month_choices'] = [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
            (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
            (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
        ]
        current_year = datetime.date.today().year
        context['year_choices'] = [str(y) for y in range(current_year, current_year - 5, -1)]
        context['day_choices'] = [str(d) for d in range(1, 32)]

        return context


# ============================================================
# DELETE VIEW
# ============================================================
class SaleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sales:sales_list')
    context_object_name = 'sale'

    def get_queryset(self):
        return super().get_queryset().filter(seller=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Venda excluída com sucesso.", extra_tags='success')
        return super().form_valid(form)


# ============================================================
# UPDATE VIEW
# ============================================================
class SaleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_update.html'
    success_url = reverse_lazy('sales:sales_list')
    login_url = 'accounts:login'
    context_object_name = 'sale'

    def get_queryset(self):
        return super().get_queryset().filter(seller=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Venda atualizada com sucesso.", extra_tags='success')
        return super().form_valid(form)
