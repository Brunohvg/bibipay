# Em apps/sales/services.py (ou onde suas funções estão)
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta, date # 👈 Garanta que 'date' está importado
from decimal import Decimal
from apps.sales.models import Sale
from apps.accounts.models import User
from django.db.models import Sum, Avg, Count
from django.utils.timezone import localdate

def create_sale(user, form):
    """
    Cria uma nova venda, associando automaticamente ao vendedor logado.
    """
    if getattr(user, 'user_type', None) != 'sellers':
        raise ValidationError("Apenas vendedores podem criar vendas.")

    try:
        sale = form.save(commit=False)
        sale.seller = user
        sale.save()
        return sale

    except Exception as e:
        raise ValidationError(f"Erro ao salvar a venda: {e}")





# ... (a função create_sale continua igual) ...


def get_sales_by_seller(seller_id: int, year: int = None, month: int = None):
    """
    Retorna as vendas de um vendedor.
    - Se 'year' e 'month' forem fornecidos, filtra por esse período.
    - Se não, retorna TODAS as vendas do vendedor.
    """
    queryset = Sale.objects.filter(seller_id=seller_id)
    
    # Filtro opcional para o dashboard
    if year and month:
        queryset = queryset.filter(date__year=year, date__month=month)
    
    # Retorna todas (ou as filtradas) ordenadas
    return queryset.order_by('-date', '-created_at')

def get_sales_dashboard_stats(seller_id: int, year: int, month: int):
    """
    Calcula as estatísticas do dashboard para um ANO e MÊS específicos.
    """
    
    # Período selecionado
    selected_period_start = date(year, month, 1)
    today = localdate() # Data de hoje (para "Hoje" e "Ontem")
    
    # Define o fim do período selecionado
    if month == today.month and year == today.year:
        selected_period_end = today
    else:
        # Pega o último dia daquele mês
        next_month_start = (selected_period_start + timedelta(days=32)).replace(day=1)
        selected_period_end = next_month_start - timedelta(days=1)

    yesterday = today - timedelta(days=1)

    # Todas as vendas do vendedor
    user_sales = Sale.objects.filter(seller_id=seller_id)

    # === Hoje === (Sempre baseado em 'today')
    today_sales = user_sales.filter(date=today)
    today_stats = today_sales.aggregate(
        count=models.Count("id"),
        total=models.Sum("total_amount"),
    )

    # === Ontem === (Sempre baseado em 'yesterday')
    yesterday_sales = user_sales.filter(date=yesterday)
    yesterday_stats = yesterday_sales.aggregate(
        count=models.Count("id"),
        total=models.Sum("total_amount"),
    )

    # === Mês Selecionado === (FILTRO PRINCIPAL)
    month_sales = user_sales.filter(
        date__gte=selected_period_start, 
        date__lte=selected_period_end
    )
    month_stats = month_sales.aggregate(
        count=models.Count("id"),
        total=models.Sum("total_amount"),
        average=models.Avg("total_amount"),
    )

    # === Cálculos finais ===
    today_amount = today_stats["total"] or Decimal("0.00")
    yesterday_amount = yesterday_stats["total"] or Decimal("0.00")
    month_amount = month_stats["total"] or Decimal("0.00")
    average_ticket = month_stats["average"] or Decimal("0.00")

    commission_rate = Decimal("0.00")
    if user_sales.exists():
        # Pega a taxa do usuário (vendedor)
        commission_rate = user_sales.first().seller.commission_rate or Decimal("0.00")
    
    month_commission = (month_amount * commission_rate) / Decimal("100")

    # === Retorno formatado ===
    return {
        "today_count": today_stats["count"] or 0,
        "today_amount": f"{today_amount:.2f}".replace(".", ","),
        "yesterday_count": yesterday_stats["count"] or 0,
        "yesterday_amount": f"{yesterday_amount:.2f}".replace(".", ","),
        "month_count": month_stats["count"] or 0,
        "month_amount": f"{month_amount:.2f}".replace(".", ","),
        "average_ticket": f"{average_ticket:.2f}".replace(".", ","),
        "month_commission": f"{month_commission:.2f}".replace(".", ","),
    }

# ... (a função get_total_sales_amount_for_active_sellers continua igual) ...
def get_total_sales_amount_for_active_sellers(seller_id: int = None) -> Decimal:
    """
    Calcula o total de vendas de todos os vendedores ativos
    ou de um vendedor específico, se informado.
    """
    sellers = User.objects.filter(user_type='sellers', is_active=True)
    if seller_id:
        sellers = sellers.filter(id=seller_id)

    total = sellers.aggregate(total=Sum('sales__total_amount'))['total'] or Decimal('0.00')
    return total