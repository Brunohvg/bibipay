from django.views.generic import TemplateView
from apps.core.decorators import redirect_by_user_type
from django.utils.decorators import method_decorator

@method_decorator(redirect_by_user_type, name='dispatch')
class DashboardView(TemplateView):

    def get_template_names(self):
        """Escolhe o template dinamicamente baseado no tipo do usuário."""
        if self.request.user.user_type == 'sellers':
            return ['dashboard/dashboard_sellers.html']
        elif self.request.user.user_type == 'boxs':
            return ['dashboard/dashboard_boxs.html']
        return ['dashboard/dashboard_admin.html']
