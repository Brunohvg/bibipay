# Em apps/dashboard/views/seller.py

from .base import BaseDashboardView
from apps.sales.services import get_sales_dashboard_stats, get_sales_by_seller
from django.utils import timezone
from datetime import date
from decimal import Decimal
from dateutil.relativedelta import relativedelta # 👈 Importe isso


class SellerDashboardView(BaseDashboardView):
    template_name = 'dashboard/sellers/dashboard_sellers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_user()
        today = timezone.localdate()

        # 1. Tenta pegar ano/mês da URL (ex: ?year=2025&month=10)
        try:
            year = int(self.request.GET.get('year', today.year))
            month = int(self.request.GET.get('month', today.month))
            selected_period_start = date(year, month, 1)
        except (ValueError, TypeError):
            # Se inválido, usa o mês atual
            year = today.year
            month = today.month
            selected_period_start = date(year, month, 1)

        # 2. Calcula URLs do navegador de mês
        prev_month_date = selected_period_start - relativedelta(months=1)
        next_month_date = selected_period_start + relativedelta(months=1)

        base_url = self.request.path
        previous_month_url = f"{base_url}?year={prev_month_date.year}&month={prev_month_date.month}"
        
        # Só permite avançar até o mês atual (não ver o futuro)
        next_month_url = None
        if next_month_date <= today.replace(day=1):
            next_month_url = f"{base_url}?year={next_month_date.year}&month={next_month_date.month}"

        # 3. Busca os dados USANDO OS PARÂMETROS de ano/mês
        stats = get_sales_dashboard_stats(user.id, year, month)
        recent_sales_list = get_sales_by_seller(user.id, year, month)
        
        # 4. Calcula comissão de cada venda
        commission_rate = getattr(user, 'commission_rate', Decimal('0.00'))
        sales_with_commission = []
        for sale in recent_sales_list:
            sale.calculated_commission = (sale.total_amount * commission_rate) / Decimal('100')
            sales_with_commission.append(sale)

        context.update({
            'seller_name': user.get_full_name() or user.email,
            'email': user.email,
            'commission_rate': commission_rate,
            
            # Dados de estatística (agora filtrados)
            'stats': stats, 
            'recent_sales': sales_with_commission,
            'total_commission': stats.get('month_commission', '0,00'),
            
            # Dados do navegador de mês (para o template)
            'selected_period_name': selected_period_start.strftime("%B").capitalize(),
            'selected_period_year': selected_period_start.year,
            'previous_month_url': previous_month_url,
            'next_month_url': next_month_url,
        })

        return context