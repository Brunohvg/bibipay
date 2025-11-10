from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from decimal import Decimal
from .models import Sale
from apps.accounts.models import User
from django.db.models import Sum

def create_sale(user, form):
    """
    Cria uma nova venda, atribuindo o vendedor corretamente.
    Lança ValidationError se algo falhar.
    """
    if not hasattr(user, 'user_type') or user.user_type != 'sellers':
        raise ValidationError("Apenas vendedores podem criar vendas.")

    try:
        # Cria a instância sem salvar ainda
        sale = form.save(commit=False)
        sale.seller = user
        sale.save()
        # form.save_m2m() # se houver campos ManyToMany
        return sale

    except Exception as e:
        raise ValidationError(f"Erro ao salvar a venda: {e}")


def get_sales_by_seller(seller_id: int, period: str = None):
    """
    Busca as vendas de um vendedor, com filtros de período opcionais.
    """
    queryset = Sale.objects.filter(seller_id=seller_id)
    today = timezone.now().date()

    if period == 'today':
        queryset = queryset.filter(date=today)
    elif period == 'week':
        week_start = today - timedelta(days=today.weekday())
        queryset = queryset.filter(date__gte=week_start)
    elif period == 'month':
        queryset = queryset.filter(date__year=today.year, date__month=today.month)
    elif period == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        queryset = queryset.filter(
            date__year=last_month.year,
            date__month=last_month.month
        )

    return queryset.order_by('-date', '-created_at')


def get_sales_dashboard_stats(seller_id: int):
    """
    Calcula todas as estatísticas para o dashboard do vendedor.
    """
    user_sales = get_sales_by_seller(seller_id)
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Estatísticas do dia
    today_sales = user_sales.filter(date=today)
    today_stats = today_sales.aggregate(
        count=models.Count('id'),
        total=models.Sum('total_amount')
    )

    # Estatísticas do mês
    month_sales = user_sales.filter(date__gte=month_start)
    month_stats = month_sales.aggregate(
        count=models.Count('id'),
        total=models.Sum('total_amount'),
        average=models.Avg('total_amount')
    )

    today_amount = today_stats['total'] or Decimal('0.00')
    month_amount = month_stats['total'] or Decimal('0.00')
    average_ticket = month_stats['average'] or Decimal('0.00')

    return {
        'today_count': today_stats['count'] or 0,
        'today_amount': f"{today_amount:.2f}".replace('.', ','),
        'month_count': month_stats['count'] or 0,
        'month_amount': f"{month_amount:.2f}".replace('.', ','),
        'average_ticket': f"{average_ticket:.2f}".replace('.', ','),
    }


def get_total_sales_amount_for_active_sellers() -> Decimal:
    """
    Calcula a soma de todas as vendas feitas por vendedores ativos.
    """
    total = User.objects.filter(
        user_type='sellers',
        is_active=True
    ).aggregate(
        total=Sum('sales__total_amount')
    )['total'] or Decimal('0.00')
    return total
