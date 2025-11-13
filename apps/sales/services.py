from django.db import models
from django.utils.timezone import localdate
from django.core.exceptions import ValidationError
from datetime import timedelta, date
from decimal import Decimal
from apps.sales.models import Sale
from apps.accounts.models import User
from apps.commissions.models import Commission


# ==========================
# CRIAÇÃO DE VENDA
# ==========================
def create_sale(user, form):
    if getattr(user, 'user_type', None) != 'sellers':
        raise ValidationError("Apenas vendedores podem criar vendas.")
    sale = form.save(commit=False)
    sale.seller = user
    sale.save()
    return sale


# ==========================
# CONSULTAS DE VENDAS
# ==========================
def get_sales_by_seller(seller_id: int, year: int = None, month: int = None):
    queryset = Sale.objects.filter(seller_id=seller_id)
    if year and month:
        queryset = queryset.filter(date__year=year, date__month=month)
    return queryset.order_by('-date', '-created_at')


# ==========================
# DASHBOARD DO VENDEDOR
# ==========================
def get_sales_dashboard_stats(seller_id: int, year: int, month: int):
    selected_period_start = date(year, month, 1)
    today = localdate()

    if month == today.month and year == today.year:
        selected_period_end = today
    else:
        next_month_start = (selected_period_start + timedelta(days=32)).replace(day=1)
        selected_period_end = next_month_start - timedelta(days=1)

    yesterday = today - timedelta(days=1)
    user_sales = Sale.objects.filter(seller_id=seller_id)

    today_stats = user_sales.filter(date=today).aggregate(
        count=models.Count("id"),
        total=models.Sum("total_amount"),
    )
    yesterday_stats = user_sales.filter(date=yesterday).aggregate(
        count=models.Count("id"),
        total=models.Sum("total_amount"),
    )
    month_sales = user_sales.filter(
        date__gte=selected_period_start,
        date__lte=selected_period_end
    )
    month_stats = month_sales.aggregate(
        count=models.Count("id"),
        total=models.Sum("total_amount"),
        average=models.Avg("total_amount"),
    )

    today_amount = today_stats["total"] or Decimal("0.00")
    yesterday_amount = yesterday_stats["total"] or Decimal("0.00")
    month_amount = month_stats["total"] or Decimal("0.00")
    average_ticket = month_stats["average"] or Decimal("0.00")

    month_commission = (
        Commission.objects.filter(sale__in=month_sales)
        .aggregate(total=models.Sum("value"))
        .get("total")
        or Decimal("0.00")
    )

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


# ==========================
# TOTAIS GERAIS (ADMIN OU SELLER)
# ==========================
def get_total_sales_amount_for_active_sellers(seller_id: int = None) -> Decimal:
    """
    Retorna o valor total de vendas de todos os vendedores ativos
    ou de um vendedor específico se informado.
    """
    queryset = Sale.objects.filter(seller__is_active=True)

    if seller_id:
        queryset = queryset.filter(seller_id=seller_id)

    total = queryset.aggregate(total=models.Sum('total_amount'))['total']
    return total or Decimal('0.00')
