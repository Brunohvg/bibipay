from .base import BaseDashboardView  # 👈 Importa a classe base
from apps.accounts.services import get_all_sellers
from apps.commissions.services import get_total_commission_value
from apps.sales.services import get_total_sales_amount_for_active_sellers


class AdminDashboardView(BaseDashboardView):
    template_name = 'dashboard/admin/dashboard_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        sellers_queryset = get_all_sellers().filter(is_active=True)
        total_vendas_calculado = get_total_sales_amount_for_active_sellers()
        total_comissao_calculado = get_total_commission_value()
        
        context.update({
            'sellers': sellers_queryset,
            'total_sellers': get_all_sellers().count(),
            'total_vendas': total_vendas_calculado,
            'total_comissao': total_comissao_calculado,
            'conversion_rate': 0,
        })
        return context
