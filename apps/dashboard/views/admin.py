from decimal import Decimal
from django.db.models import Sum, Avg, Max
from .base import BaseDashboardView
from apps.accounts.services import get_all_sellers
from apps.sales.services import get_total_sales_amount_for_active_sellers
from apps.commissions.services import get_total_commission_value
from apps.sales.models import Sale
from apps.commissions.models import Commission


class AdminDashboardView(BaseDashboardView):
    template_name = 'dashboard/admin/dashboard_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sellers = get_all_sellers().filter(is_active=True)
        total_sellers = get_all_sellers().count()
        active_sellers = sellers.count()

        # Totais gerais
        total_vendas = get_total_sales_amount_for_active_sellers()
        total_comissao = get_total_commission_value()

        # Métricas agregadas
        all_sales = Sale.objects.all()
        avg_ticket = all_sales.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')
        top_sale_value = all_sales.aggregate(max=Max('total_amount'))['max'] or Decimal('0.00')

        # Identifica o vendedor com mais vendas em valor total
        top_seller_data = (
            Sale.objects.values('seller__first_name', 'seller__last_name')
            .annotate(total_vendas=Sum('total_amount'))
            .order_by('-total_vendas')
            .first()
        )
        top_seller_name = (
            f"{top_seller_data['seller__first_name']} {top_seller_data['seller__last_name']}"
            if top_seller_data else "—"
        )

        # Taxa de conversão (apenas para exibição)
        conversion_rate = (
            round((active_sellers / total_sellers) * 100, 2) if total_sellers > 0 else 0
        )

        # Calcula totais individuais de cada vendedor (para o ranking)
        sellers_data = []
        for seller in sellers:
            seller_sales = Sale.objects.filter(seller=seller)
            sales_total = (
                seller_sales.aggregate(total=Sum('total_amount'))['total']
                or Decimal('0.00')
            )
            sales_count = seller_sales.count() # <-- NOVO
            
            commission_total = (
                Commission.objects.filter(sale__seller=seller).aggregate(total=Sum('value'))['total']
                or Decimal('0.00')
            )
            
            sellers_data.append({
                'id': seller.id,
                'first_name': seller.first_name,
                'last_name': seller.last_name,
                'email': seller.email, # <-- NOVO
                'sales_total': sales_total,
                'sales_count': sales_count, # <-- NOVO
                'commission_total': commission_total,
            })

        # Ordena os vendedores pelo total de vendas (opcional, mas recomendado)
        sellers_data = sorted(sellers_data, key=lambda s: s['sales_total'], reverse=True)

        context.update({
            'sellers': sellers_data,
            'total_sellers': total_sellers,
            'total_vendas': Decimal(total_vendas).quantize(Decimal('0.00')),
            'total_comissao': Decimal(total_comissao).quantize(Decimal('0.00')),
            'avg_ticket': f"{avg_ticket:.2f}".replace('.', ','),
            'top_seller_name': top_seller_name,
            'top_sale_value': f"{top_sale_value:.2f}".replace('.', ','), # Esta variável não está sendo usada no template
            'conversion_rate': conversion_rate,
        })

        return context