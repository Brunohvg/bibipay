from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.commissions import services as commission_services
import csv # Para gerar o relatório para a contabilidade

class CommissionTrackingView(LoginRequiredMixin, View):
    template_name = "commissions/commissions.html" # Novo nome do template

    def get(self, request, *args, **kwargs):
        # 1. Busca os totais para os cards
        totals = commission_services.get_commission_totals_for_cards()
        
        # 2. Busca a lista principal (SÓ o que está pronto para pagar)
        payment_groups = commission_services.get_commissions_ready_for_payment()

        context = {
            'totals': totals,
            'payment_groups': payment_groups
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Processa o "Lote de Pagamento" para a contabilidade.
        """
        # Pega os IDs dos VENDEDORES selecionados
        seller_ids_selected = request.POST.getlist('selected_sellers')
        
        if not seller_ids_selected:
            messages.error(request, "Nenhum vendedor foi selecionado.")
            # Ajuste o nome da URL se for diferente
            return redirect('commissions:tracking') 

        # --- 1. Busca os dados para o CSV ---
        all_groups = commission_services.get_commissions_ready_for_payment()
        groups_to_pay = [g for g in all_groups if str(g['seller_id']) in seller_ids_selected]
        
        if not groups_to_pay:
             messages.error(request, "Vendedores selecionados não têm comissões prontas.")
             return redirect('commissions:tracking')

        # --- 2. Cria a resposta CSV ---
        response = HttpResponse(content_type='text/csv')
        filename = f"relatorio_pagamento_{timezone.now().date()}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['ID_Vendedor', 'Nome_Vendedor', 'Valor_Total_Pagar'])
        
        all_commission_ids_to_mark_paid = []
        
        for group in groups_to_pay:
            writer.writerow([
                group['seller_id'], 
                group['seller_name'], 
                group['total_value']
            ])
            # Coleta todos os IDs de comissão para marcar como pagos
            all_commission_ids_to_mark_paid.extend(group['commission_ids'])

        # --- 3. Marcar comissões como PAGAS no banco ---
        commission_services.mark_commissions_as_paid(all_commission_ids_to_mark_paid)
        
        # --- 4. Retorna o arquivo CSV para o Admin ---
        # A mensagem de sucesso não será vista (pois é um download),
        # mas é bom ter o log. O download é a confirmação.
        messages.success(request, "Relatório gerado! As comissões foram marcadas como pagas.")
        return response
    

# apps/commissions/views.py

from django.views import View # 👈 MUDANÇA: Use View em vez de ListView
from django.shortcuts import render 
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.commissions import services as commission_services
# ATENÇÃO: Verifique se você tem esta função em algum lugar
from apps.accounts.services import get_all_sellers 

class CommissionHistoryView(LoginRequiredMixin, View):
    template_name = "commissions/historico.html"
    login_url = 'accounts:login'

    def get(self, request, *args, **kwargs):
        # 1. Armazena os filtros da URL
        seller_id = request.GET.get('seller', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        
        # 2. Chama o serviço para obter os totais AGREGADOS
        summary_data = commission_services.get_paid_commissions_summary(
            seller_id=seller_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # 3. Calcula os totais globais da página
        total_commission_filtered = sum(item['total_commission'] for item in summary_data)
        total_sales_filtered = sum(item['total_sales'] for item in summary_data)

        context = {
            'summary_data': summary_data, # O NOVO CONTEXTO COM DADOS AGRUPADOS
            'all_sellers': get_all_sellers(),
            'selected_seller': seller_id,
            'selected_start_date': start_date,
            'selected_end_date': end_date,
            'total_commission_filtered': total_commission_filtered,
            'total_sales_filtered': total_sales_filtered,
        }
        
        # 4. Renderiza manualmente, já que não é um ListView
        return render(request, self.template_name, context)