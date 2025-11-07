from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from apps.core.decorators import redirect_by_user_type
from apps.accounts.models import User


@method_decorator(redirect_by_user_type, name='dispatch')
class BaseDashboardView(TemplateView):
    """Classe base para dashboards. Define comportamento comum."""

    def get_user(self):
        return self.request.user


class AdminDashboardView(BaseDashboardView):
    template_name = 'dashboard/dashboard_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sellers = User.objects.filter(user_type='sellers', is_active=True)
        context.update({
            'sellers': sellers,
            'total_sellers': sellers.count(),
            'total_vendas': 0,
            'total_comissao': 0,
            'total_links': 0,
        })
        return context


class SellerDashboardView(BaseDashboardView):
    template_name = 'dashboard/dashboard_sellers.html'

    def get_context_data(self, **kwargs):
        user = self.get_user()
        context = super().get_context_data(**kwargs)
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
