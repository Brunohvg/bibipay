from django.shortcuts import get_object_or_404
from .models import Commission  # Importa o modelo de comissão

# ==========================
# FUNÇÕES DE LEITURA (Read)
# ==========================    

def get_commission_by_id(commission_id: int) -> Commission:
    """
    Busca uma comissão específica pelo seu ID.
    
    Se não encontrar, levanta um erro 404.

    Args:
        commission_id (int): A Chave Primária (pk) da comissão a ser buscada.

    Returns:
        Commission: O objeto Commission encontrado.

    Raises:
        Http404: Se nenhuma comissão for encontrada com esse ID.
    """
    commission = get_object_or_404(Commission, pk=commission_id)
    return commission


def get_all_commissions() -> list[Commission]:
    """
    Busca todas as comissões cadastradas no sistema.

    Returns:
        list[Commission]: Uma lista de objetos Commission.
    """
    return list(Commission.objects.all())


# apps/commissions/services.py
from apps.commissions.models import Commission
from django.db.models import Sum
from decimal import Decimal

def get_total_commission_value() -> Decimal:
    """Calcula e retorna o valor total de todas as comissões não pagas."""
    # Agrega o valor total de comissões não pagas
    total = Commission.objects.filter(paid=False).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    return total