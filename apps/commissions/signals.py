from turtle import up
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sales.models import Sale
from .models import Commission


@receiver(post_save, sender=Sale)
def create_or_update_commission(sender, instance, created, **kwargs):
    seller = instance.seller

    if not seller or not hasattr(seller, 'commission_rate'):
        return

    if created:
        # VENDA NOVA → cria comissão
        commission = Commission.objects.create(
            sale=instance,
            seller=seller,
            percentage=seller.commission_rate or 0
        )
        commission.calculate_value()
        commission.save()
        return

    # VENDA ATUALIZADA → atualiza comissão existente
    try:
        commission = Commission.objects.get(sale=instance)
        commission.percentage = seller.commission_rate or commission.percentage
        commission.calculate_value()
        commission.save()
    except Commission.DoesNotExist:
        # Se por algum motivo não existir, cria
        commission = Commission.objects.create(
            sale=instance,
            seller=seller,
            percentage=seller.commission_rate or 0
        )
        commission.calculate_value()
        commission.save()
