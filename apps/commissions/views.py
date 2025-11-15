from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

# Importações de Serviços e Modelos
from apps.commissions import services as commission_services
# ATENÇÃO: Assumimos que esta função existe e retorna todos os vendedores para filtros
from apps.accounts.services import get_all_sellers 
import csv 


# =========================================================================
# 1. VIEW DE ACOMPANHAMENTO (TRACKING)
# Responsável por listar comissões pendentes, gerar relatórios e dar baixa.
# =========================================================================
class CommissionTrackingView(LoginRequiredMixin, View):
    """
    Exibe a lista de comissões prontas para pagamento (paid=False), 
    agrupadas por vendedor. Processa a ação de gerar relatório CSV e 
    marcar as comissões selecionadas como pagas (paid=True).
    """
    template_name = "commissions/acompanhamento.html" 
    login_url = 'accounts:login'

    def get(self, request, *args, **kwargs):
        """ Carrega os dados para a tela principal (cards e tabela de grupos). """
        
        # 1. Busca os totais para os cards (Total a Pagar, Pago no Mês, etc.)
        totals = commission_services.get_commission_totals_for_cards()
        
        # 2. Busca a lista principal: Comissões prontas para pagar, agrupadas por vendedor.
        payment_groups = commission_services.get_commissions_ready_for_payment()

        context = {
            'totals': totals,
            'payment_groups': payment_groups
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """ 
        Processa o "Lote de Pagamento" (Gera CSV e Marca como Pago).
        """
        seller_ids_selected = request.POST.getlist('selected_sellers')
        
        if not seller_ids_selected:
            messages.error(request, "Nenhum vendedor foi selecionado.")
            return redirect('commissions:tracking') 

        # --- 1. Busca os dados COMPLETOs APENAS dos grupos selecionados ---
        all_groups = commission_services.get_commissions_ready_for_payment()
        groups_to_pay = [g for g in all_groups if str(g['seller_id']) in seller_ids_selected]
        
        if not groups_to_pay:
            messages.error(request, "Vendedores selecionados não têm comissões prontas.")
            return redirect('commissions:tracking')

        # --- 2. Cria a resposta CSV e coleta todos os IDs ---
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
                group['total_commission'] # O valor total da comissão para o holerite
            ])
            # Coleta todos os IDs de comissão individuais para dar baixa no DB
            all_commission_ids_to_mark_paid.extend(group['commission_ids'])

        # --- 3. Marcar comissões como PAGAS no banco ---
        # A baixa é dada no banco ANTES de enviar o CSV, garantindo que o sistema não perca o estado.
        commission_services.mark_commissions_as_paid(all_commission_ids_to_mark_paid)
        
        # --- 4. Retorna o arquivo CSV (que é a confirmação visual da ação) ---
        messages.success(request, "Relatório gerado! As comissões foram marcadas como pagas.")
        return response


# =========================================================================
# 2. VIEW DE HISTÓRICO (HISTORY)
# Responsável por listar o histórico consolidado de comissões pagas.
# =========================================================================
class CommissionHistoryView(LoginRequiredMixin, View):
    """
    Exibe o histórico de comissões já pagas. Os dados são agregados 
    por Vendedor e Mês de Pagamento para visualização consolidada.
    """
    template_name = "commissions/historico.html"
    login_url = 'accounts:login'

    def get(self, request, *args, **kwargs):
        """ Carrega os dados consolidados e aplica os filtros GET. """
        
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
        
        # 3. Calcula os totais globais da página (para o card de resumo no template)
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
        
        return render(request, self.template_name, context)