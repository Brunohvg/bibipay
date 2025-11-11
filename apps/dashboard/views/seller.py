from .base import BaseDashboardView  # 👈 Importa daqui

from apps.accounts.services import get_all_sellers
from apps.commissions.services import get_total_commission_value
from apps.sales.services import get_total_sales_amount_for_active_sellers


class SellerDashboardView(BaseDashboardView):
    template_name = 'dashboard/dashboard_sellers.html'

    def get_context_data(self, **kwargs):
        user = self.get_user()
        context = super().get_context_data(**kwargs)

        # Aqui você chamaria services.get_sales_dashboard_stats(user.id)
        # e preencheria o restante do contexto
        context.update({
            'seller_name': user.get_full_name() or user.email,
            'email': user.email,
            'commission_rate': getattr(user, 'commission_rate', 0),
            'total_vendas': 0,
            'total_comissao': 0,
            'total_links': 0,
        })
        return context
