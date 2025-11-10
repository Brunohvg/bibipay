from datetime import timedelta
from decimal import Decimal
from django.db import models, IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from .models import Sale
from django.db.models import Sum

# =======================
# 🔹 CRUD E REGRAS DE NEGÓCIO
# =======================
def create_sale(user, form):
    """
    Cria uma nova venda, atribuindo o vendedor corretamente.
    Lança ValidationError se algo falhar.
    """
    if not hasattr(user, 'user_type') or user.user_type != 'sellers':
        raise ValidationError("Apenas vendedores podem criar vendas.")

    try:
        sale = form.save(commit=False)
        sale.seller = user

        # Define a data se o form não trouxe
        sale_date = getattr(sale, 'sale_date', None) or timezone.localdate()
        sale.sale_date = sale_date

        # Calcula comissão se o vendedor tiver porcentagem definida
        if hasattr(user, 'percentage') and user.percentage:
            sale.percentage = user.percentage
            sale.commission_value = sale.value * (user.percentage / 100)
        else:
            sale.percentage = 0
            sale.commission_value = 0

        sale.save()
        return sale

    except IntegrityError:
        raise ValidationError("Já existe uma venda lançada para essa data.")
    except Exception as e:
        raise ValidationError(f"Erro ao salvar: {e}")


# =======================
# 🔹 CONSULTAS E FILTROS
# =======================
def get_sales_by_seller(seller_id: int, period: str = None):
    """
    Retorna as vendas de um vendedor, com filtros opcionais de período.
    """
    queryset = Sale.objects.filter(seller_id=seller_id)
    today = timezone.now().date()

    if period == 'today':
        queryset = queryset.filter(sale_date=today)
    elif period == 'week':
        week_start = today - timedelta(days=today.weekday())
        queryset = queryset.filter(sale_date__gte=week_start)
    elif period == 'month':
        queryset = queryset.filter(
            sale_date__year=today.year,
            sale_date__month=today.month
        )
    elif period == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        queryset = queryset.filter(
            sale_date__year=last_month.year,
            sale_date__month=last_month.month
        )

    return queryset.order_by('-sale_date', '-created_at')


# =======================
# 🔹 DASHBOARD DE VENDAS
# =======================
def get_sales_dashboard_stats(seller_id: int):
    """
    Calcula as estatísticas de vendas do vendedor (dia, mês e ticket médio).
    """
    user_sales = get_sales_by_seller(seller_id)
    today = timezone.now().date()
    month_start = today.replace(day=1)

    today_sales = user_sales.filter(sale_date=today)
    today_stats = today_sales.aggregate(
        count=models.Count('id'),
        total=models.Sum('value')
    )

    month_sales = user_sales.filter(sale_date__gte=month_start)
    month_stats = month_sales.aggregate(
        count=models.Count('id'),
        total=models.Sum('value'),
        average=models.Avg('value')
    )

    # Formata dados numéricos
    today_total = today_stats['total'] or Decimal('0.00')
    month_total = month_stats['total'] or Decimal('0.00')
    avg_ticket = month_stats['average'] or Decimal('0.00')

    return {
        'today_count': today_stats['count'] or 0,
        'today_amount': f"{today_total:.2f}".replace('.', ','),
        'month_count': month_stats['count'] or 0,
        'month_amount': f"{month_total:.2f}".replace('.', ','),
        'average_ticket': f"{avg_ticket:.2f}".replace('.', ','),
    }


# =======================
# 🔹 TOTAL GERAL DE VENDAS
# =======================
def get_total_sales_amount_for_active_sellers() -> Decimal:
    """
    Calcula a soma total das vendas feitas por vendedores ativos.
    """
    total = User.objects.filter(
        user_type='sellers',
        is_active=True
    ).aggregate(
        total=Sum('sales__value')
    )['total'] or Decimal('0.00')

    return total
