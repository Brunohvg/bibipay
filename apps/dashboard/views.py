# apps/dashboard/views.py
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

# IMPORTAÇÕES DO SERVICE LAYER
from apps.core.decorators import redirect_by_user_type
from apps.accounts.services import get_all_sellers
from apps.commissions.services import get_total_commission_value
from apps.sales.services import get_total_sales_amount_for_active_sellers

# ========================================================
# VIEWS
# ========================================================

@method_decorator(redirect_by_user_type, name='dispatch')
class BaseDashboardView(TemplateView, LoginRequiredMixin):
    """Classe base para dashboards."""
    login_url = 'accounts:login'

    def get_user(self):
        return self.request.user


class AdminDashboardView(BaseDashboardView):
    template_name = 'dashboard/dashboard_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. VISÃO DO ADMIN: Vendedores Ativos
        sellers_queryset = get_all_sellers().filter(is_active=True)
        
        # 2. VISÃO DO ADMIN: Totais Globais (Chamadas aos Services)
        total_vendas_calculado = get_total_sales_amount_for_active_sellers()
        total_comissao_calculado = get_total_commission_value()
        
        # 3. CONTEXTO
        context.update({
            'sellers': sellers_queryset,
            'total_sellers': get_all_sellers().count(), # Total absoluto (ativos + inativos)
            
            # Dados vindo dos Services
            'total_vendas': total_vendas_calculado,
            'total_comissao': total_comissao_calculado,
            
            # Placeholders
            'conversion_rate': 0, 
        })
        return context


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


class BoxDashboardView(BaseDashboardView):
    template_name = 'dashboard/dashboard_boxs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mensagem'] = 'Bem-vindo ao painel da BOX!'
        return context