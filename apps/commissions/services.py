# apps/commissions/services.py
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from decimal import Decimal
from apps.commissions.models import Commission


# ==========================
# FUNÇÕES DE LEITURA (Read)
# ==========================    

def get_commission_by_id(commission_id: int) -> Commission:
    """
    Retorna uma comissão específica pelo seu ID.
    Lança 404 se não for encontrada.
    """
    return get_object_or_404(Commission, pk=commission_id)


def get_all_commissions() -> list[Commission]:
    """
    Retorna todas as comissões cadastradas.
    """
    return list(Commission.objects.all())


def get_total_commission_value(seller_id: int | None = None) -> Decimal:
    """
    Retorna o valor total de todas as comissões não pagas.
    Se um seller_id for informado, filtra apenas por esse vendedor.
    """
    queryset = Commission.objects.filter(paid=False)

    if seller_id:
        queryset = queryset.filter(sale__seller_id=seller_id)

    total = queryset.aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    return total
