# apps/commissions/services.py

from decimal import Decimal
from django.db.models import Sum, Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

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


def get_commission_totals_for_cards() -> dict:
    """
    Calcula os totais para os cards da página de Acompanhamento.
    """
    today = timezone.now().date()
    
    total_ready = Commission.objects.filter(
        paid=False
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')

    total_paid_month = Commission.objects.filter(
        paid=True,
        paid_at__year=today.year,
        paid_at__month=today.month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')

    return {
        'ready_total': total_ready,
        'paid_month_total': total_paid_month,
    }


def get_commissions_ready_for_payment() -> list[dict]:
    """
    Retorna comissões NÃO PAGAS, agrupadas por vendedor.
    """
    commissions = Commission.objects.filter(
        paid=False
    ).select_related('sale__seller')
    
    grouped = commissions.values(
        'sale__seller_id', 
        'sale__seller__first_name', 
        'sale__seller__last_name'
    ).annotate(
        total_value=Sum('value'),
        commission_count=Count('id')
    ).order_by('-total_value')
    
    payment_groups = []

    for group in grouped:
        seller_id = group['sale__seller_id']
        
        commission_ids = list(
            commissions.filter(sale__seller_id=seller_id)
            .values_list('id', flat=True)
        )
        
        payment_groups.append({
            'seller_id': seller_id,
            'seller_name': f"{group['sale__seller__first_name']} {group['sale__seller__last_name']}",
            'total_value': group['total_value'],
            'commission_count': group['commission_count'],
            'commission_ids': commission_ids,
        })

    return payment_groups


# ==========================
# FUNÇÕES DE ESCRITA (Write)
# ========================== 

def mark_commissions_as_paid(commission_ids: list[int]) -> int:
    """
    Marca uma lista de IDs de comissões como pagas e define o paid_at.
    Retorna a quantidade de atualizações realizadas.
    """
    updated_count = Commission.objects.filter(
        id__in=commission_ids,
        paid=False
    ).update(
        paid=True,
        paid_at=timezone.now()
    )
    return updated_count

def get_paid_commissions_history(seller_id=None, start_date=None, end_date=None):
    """
    Retorna todas as comissões PAGAS, filtradas por vendedor e data de pagamento.
    """
    queryset = Commission.objects.filter(
        paid=True
    ).select_related('sale__seller').order_by('-paid_at') # Ordena pelo mais recente PAGO

    if seller_id:
        queryset = queryset.filter(sale__seller_id=seller_id)
    
    # Filtra pela data em que a comissão foi paga (paid_at)
    if start_date:
        queryset = queryset.filter(paid_at__date__gte=start_date)
        
    if end_date:
        queryset = queryset.filter(paid_at__date__lte=end_date)
        
    return queryset


from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth # 👈 NOVO IMPORT
# ... (mantenha os outros imports e funções)

# ...

def get_paid_commissions_summary(seller_id=None, start_date=None, end_date=None):
    """
    Retorna o histórico de comissões PAGAS, agrupado por Vendedor e Mês de Pagamento.
    """
    queryset = Commission.objects.filter(
        paid=True
    ).select_related('sale__seller')

    if seller_id:
        queryset = queryset.filter(sale__seller_id=seller_id)
    
    # Filtra pelo campo pago (paid_at)
    if start_date:
        queryset = queryset.filter(paid_at__date__gte=start_date)
        
    if end_date:
        queryset = queryset.filter(paid_at__date__lte=end_date)
        
    # Agrupamento e Agregação
    summary = queryset.annotate(
        # Cria um novo campo 'payment_month' truncando o 'paid_at' para o início do mês
        payment_month=TruncMonth('paid_at')
    ).values(
        'sale__seller_id', 
        'sale__seller__first_name', 
        'sale__seller__last_name',
        'payment_month'
    ).annotate(
        total_commission=Sum('value'),
        total_sales=Sum('sale__total_amount'),
        commission_count=Count('id')
    ).order_by('-payment_month', 'sale__seller__first_name')

    return summary