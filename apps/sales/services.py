# apps/sales/services.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import Sale

def create_sale(user, form):
    """
    Cria uma nova venda, atribuindo o vendedor corretamente.
    Lança ValidationError se algo falhar.
    """
    try:
        # Pega a instância do modelo do formulário, mas não salva ainda
        sale = form.save(commit=False) 
        
        # Atribui o vendedor (lógica de negócio)
        sale.seller = user 
        
        # Agora salva no banco
        sale.save() 
        
        # (Opcional) Salva relações Many-to-Many se houver
        # form.save_m2m() 
        
        return sale
    except Exception as e:
        # Captura qualquer erro de banco (como a constraint 'unique_sale_per_seller_per_day')
        # e o transforma em um erro de validação amigável.
        raise ValidationError(f"Erro ao salvar: {e}")

def get_sales_by_seller(seller_id: int, period: str = None):
    """
    Busca as vendas de um vendedor, com filtros de período opcionais.
    """
    queryset = Sale.objects.filter(seller_id=seller_id)
    
    # ======= LÓGICA DE FILTRO MOVEMIDA DA VIEW PARA CÁ =======
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
    user_sales = get_sales_by_seller(seller_id) # Reutiliza a função base
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
    
    # Formata valores
    today_amount = today_stats['total'] or 0
    month_amount = month_stats['total'] or 0
    average_ticket = month_stats['average'] or 0

    return {
        'today_count': today_stats['count'] or 0,
        'today_amount': f"{today_amount:.2f}".replace('.', ','),
        'month_count': month_stats['count'] or 0,
        'month_amount': f"{month_amount:.2f}".replace('.', ','),
        'average_ticket': f"{average_ticket:.2f}".replace('.', ','),
    }

# apps/sales/services.py
from apps.accounts.models import User
from django.db.models import Sum
from decimal import Decimal

def get_total_sales_amount_for_active_sellers() -> Decimal:
    """Calcula a soma de todas as vendas feitas por vendedores ativos."""
    # O QuerySet complexo fica aqui, no Service
    total = User.objects.filter(
        user_type='sellers', 
        is_active=True
    ).aggregate(
        total=Sum('sales__total_amount')
    )['total'] or Decimal('0.00')
    return total