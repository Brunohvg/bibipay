from apps.sales.models import Sale
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Commission
@receiver(post_save, sender=Sale)
def create_commission_for_sale(sender, instance, created, **kwargs):
    """
    Sinal que cria uma comissão automaticamente quando uma nova venda é criada.
    A comissão é calculada com base na taxa do vendedor associado à venda.
    """
    if created:
        seller = instance.seller  # Supondo que a venda tenha um campo 'seller'
        if seller and hasattr(seller, 'commission_rate'):
            commission = Commission.objects.create(
                seller=seller,
                sale=instance,
                percentage=seller.commission_rate
            )
            commission.calculate_value()
            commission.save()