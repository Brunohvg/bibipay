from django.apps import AppConfig


class CommissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.commissions'
    verbose_name = 'Commissions'

    def ready(self):
        # Importa os sinais para garantir que eles sejam registrados
        import apps.commissions.signals

