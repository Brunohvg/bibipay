from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sales.models import Sale
from .models import Commission

@receiver(post_save, sender=Sale)
def create_commission_for_sale(sender, instance, created, **kwargs):
    """
    Cria automaticamente a comissão ao registrar uma nova venda.
    A lógica de cálculo já está no próprio model Commission.
    """
    if not created:
        return

    seller = instance.seller

    # só cria se houver vendedor válido
    if not seller or not hasattr(seller, 'commission_rate'):
        return

    # evita duplicação se o sinal for chamado mais de uma vez
    commission, created_commission = Commission.objects.get_or_create(
        sale=instance,
        defaults={
            'seller': seller,
            'percentage': seller.commission_rate or 0,
        },
    )

    # garante que o valor seja calculado e salvo
    commission.calculate_value()
    commission.save()
