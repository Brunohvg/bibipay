from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Max, Q
from django.utils import timezone
from .base import BaseDashboardView
from apps.accounts.services import get_all_sellers
from apps.sales.models import Sale
from apps.commissions.models import Commission


class AdminDashboardView(BaseDashboardView):
    template_name = 'dashboard/admin/dashboard_admin.html'

    def get_date_range(self):
        """Retorna o intervalo de datas baseado no período selecionado"""
        period = self.request.GET.get('period', 'month')  # Padrão: mês atual
        today = timezone.now().date()
        
        if period == 'today':
            start_date = today
            end_date = today
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())  # Segunda-feira
            end_date = start_date + timedelta(days=6)  # Domingo
        elif period == 'month':
            start_date = today.replace(day=1)
            end_date = today  # Mês até a data (Month to Date)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        elif period == 'custom':
            start_date_str = self.request.GET.get('start')
            end_date_str = self.request.GET.get('end')
            
            if start_date_str and end_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    start_date = today.replace(day=1)
                    end_date = today
            else:
                start_date = today.replace(day=1)
                end_date = today
        else:
            # Padrão: mês atual
            start_date = today.replace(day=1)
            end_date = today
        
        return start_date, end_date
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtém o intervalo de datas
        start_date, end_date = self.get_date_range()
        period = self.request.GET.get('period', 'month')

        # Filtro de data para vendas
        # ⬇️ CORREÇÃO PRINCIPAL AQUI ⬇️
        date_filter = Q(date__gte=start_date) & Q(date__lte=end_date)

        sellers = get_all_sellers().filter(is_active=True)
        total_sellers = get_all_sellers().count()
        active_sellers = sellers.count()

        # Totais gerais filtrados por data
        all_sales = Sale.objects.filter(date_filter)
        total_vendas = all_sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        total_comissao = Commission.objects.filter(
            sale__in=all_sales
        ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')

        # Métricas agregadas
        avg_ticket = all_sales.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')
        top_sale_value = all_sales.aggregate(max=Max('total_amount'))['max'] or Decimal('0.00')
        total_sales_count = all_sales.count()

        # Identifica o vendedor com mais vendas em valor total
        top_seller_data = (
            all_sales.values('seller__first_name', 'seller__last_name')
            .annotate(total_vendas=Sum('total_amount'))
            .order_by('-total_vendas')
            .first()
        )
        top_seller_name = (
            f"{top_seller_data['seller__first_name']} {top_seller_data['seller__last_name']}"
            if top_seller_data else "—"
        )

        # Taxa de conversão (Ativos / Total)
        conversion_rate = (
            round((active_sellers / total_sellers) * 100, 2) if total_sellers > 0 else 0
        )

        # Calcula totais individuais de cada vendedor no período
        sellers_data = []
        for seller in sellers:
            seller_sales = Sale.objects.filter(seller=seller).filter(date_filter)
            sales_total = (
                seller_sales.aggregate(total=Sum('total_amount'))['total']
                or Decimal('0.00')
            )
            sales_count = seller_sales.count()
            
            commission_total = (
                Commission.objects.filter(
                    sale__seller=seller,
                    sale__in=seller_sales
                ).aggregate(total=Sum('value'))['total']
                or Decimal('0.00')
            )
            
            if sales_count > 0:
                sellers_data.append({
                    'id': seller.id,
                    'first_name': seller.first_name,
                    'last_name': seller.last_name,
                    'email': seller.email,
                    'sales_total': sales_total,
                    'sales_count': sales_count,
                    'commission_total': commission_total,
                })

        # Ordena os vendedores pelo total de vendas
        sellers_data = sorted(sellers_data, key=lambda s: s['sales_total'], reverse=True)

        # Calcula variação em relação ao período anterior
        previous_start = start_date - (end_date - start_date + timedelta(days=1))
        previous_end = start_date - timedelta(days=1)
        
        # ⬇️ CORREÇÃO PRINCIPAL AQUI ⬇️
        previous_sales = Sale.objects.filter(
            date__gte=previous_start,
            date__lte=previous_end
        )
        previous_total = previous_sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Calcula percentual de variação
        if previous_total > 0:
            sales_variation = round(((total_vendas - previous_total) / previous_total) * 100, 1)
        else:
            sales_variation = 0 if total_vendas == 0 else 100

        # Média diária
        days_in_period = (end_date - start_date).days + 1
        daily_average = round(total_sales_count / days_in_period, 1) if days_in_period > 0 else 0

        context.update({
            'sellers': sellers_data,
            'total_sellers': total_sellers,
            'active_sellers': active_sellers,
            'total_vendas': total_vendas.quantize(Decimal('0.01')),
            'total_comissao': total_comissao.quantize(Decimal('0.01')),
            'avg_ticket': f"{avg_ticket:.2f}".replace('.', ','),
            'top_seller_name': top_seller_name,
            'top_sale_value': f"{top_sale_value:.2f}".replace('.', ','),
            'conversion_rate': conversion_rate,
            'total_sales_count': total_sales_count,
            'sales_variation': sales_variation,
            'daily_average': daily_average,
            'current_period': period,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'start_date_display': start_date.strftime('%d/%m/%Y'),
            'end_date_display': end_date.strftime('%d/%m/%Y'),
        })

        return context