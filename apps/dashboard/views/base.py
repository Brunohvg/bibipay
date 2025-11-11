from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.decorators import redirect_by_user_type


@method_decorator(redirect_by_user_type, name='dispatch')
class BaseDashboardView(LoginRequiredMixin, TemplateView):
    """Classe base para dashboards."""
    login_url = 'accounts:login'

    def get_user(self):
        return self.request.user
