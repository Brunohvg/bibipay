from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sales.models import Sale
from .models import Commission


@receiver(post_save, sender=Sale)
def create_commission_for_sale(sender, instance, created, **kwargs):
    """
    Cria automaticamente a comissão ao registrar uma nova venda.
    """
    if not created:
        return

    seller = instance.seller

    if not seller or not hasattr(seller, 'commission_rate'):
        return

    # Evita duplicação
    commission, _ = Commission.objects.get_or_create(
        sale=instance,
        defaults={
            'seller': seller,
            'percentage': seller.commission_rate or 0,
        },
    )

    commission.calculate_value()
    commission.save()
