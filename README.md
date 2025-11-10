from pathlib import Path

readme_content = """# 🧠 Sistema de Gestão de Comissões Django

Este projeto implementa um fluxo completo de **registro de vendas, cálculo automático de comissões e dashboards** distintos para administradores e vendedores.

---

## ⚙️ Aliases Django + UV

Esses aliases facilitam o uso dos principais comandos Django quando executados com o `uv`.

### 🧩 Como configurar

Adicione as linhas abaixo no seu arquivo `~/.bashrc` (ou `~/.zshrc` se usar zsh):

```bash
# Ativar alterações
source ~/.bashrc

# Inicia o servidor de desenvolvimento
alias run="uv run manage.py runserver"

# Aplica migrações no banco de dados
alias mig="uv run manage.py migrate"

# Cria novas migrações a partir dos models
alias makemig="uv run manage.py makemigrations"

# Cria um novo superusuário
alias su="uv run manage.py createsuperuser"

# Abre o shell interativo do Django
alias sh="uv run manage.py shell"
Comandos práticos:

bash
Sempre exibir os detalhes

Copiar código
run      # Inicia servidor
mig      # Aplica migrações
makemig  # Cria migrações
su       # Cria superusuário
sh       # Abre shell
💸 Fluxo de Dados — Sistema de Comissões
1️⃣ Registro da Venda (apps/sales)
O vendedor acessa a SaleCreateView, preenche a data e o valor vendido.
A view chama o service create_sale(user, form) que cria o registro no model Sale.

python
Sempre exibir os detalhes

Copiar código
Sale.objects.create(
    seller=request.user,
    date=form.cleaned_data['date'],
    total_amount=form.cleaned_data['total_amount']
)
📎 Regra de negócio: só é permitida 1 venda por dia por vendedor (UniqueConstraint).

2️⃣ Geração Automática da Comissão (apps/commissions)
Ao salvar uma nova venda, o sistema cria automaticamente a comissão:

python
Sempre exibir os detalhes

Copiar código
Commission.objects.create(
    seller=sale.seller,
    sale=sale,
    percentage=sale.seller.commission_rate or 0
)
O cálculo é feito no próprio save() do model:

python
Sempre exibir os detalhes

Copiar código
self.value = (sale.total_amount * percentage) / 100
💰 Assim, toda comissão já nasce vinculada e calculada à venda.

3️⃣ Painel do Vendedor (SellerDashboardView)
Mostra informações consolidadas:

Total de vendas → get_sales_dashboard_stats(user.id)

Total de comissões → get_total_commission_value(user.id)

Últimas vendas → get_sales_by_seller(user.id)

💡 Toda a lógica vem dos services, sem regras dentro das views.

4️⃣ Painel do Administrador (AdminDashboardView)
O admin visualiza e gerencia:

Lista geral de vendedores → get_all_sellers()

Soma global de vendas → get_total_sales_amount_for_active_sellers()

Soma total de comissões → get_total_commission_value()

Ranking dos vendedores e relatórios filtráveis

💡 Gráficos podem ser adicionados com Chart.js ou Recharts.

5️⃣ Pagamento de Comissão (apps/commissions)
O admin pode marcar uma comissão como paga:

python
Sempre exibir os detalhes

Copiar código
commission.paid = True
commission.save()
Automaticamente o campo paid_at é preenchido:

python
Sempre exibir os detalhes

Copiar código
paid_at = timezone.now()
📅 Todo o histórico de pagamentos é rastreável.

🧱 Estrutura dos Apps
App	Responsabilidade	Model Principal
accounts	Usuários, autenticação e perfis (admin/seller)	User
sales	Registro das vendas	Sale
commissions	Cálculo e status das comissões	Commission
dashboard	Telas e dashboards (admin/seller)	—
core	Utilidades, base, decorators e services	BaseModel

🔥 Resumo Seco
✅ Vendedor lança venda
💰 Sistema gera comissão automaticamente
📊 Vendedor acompanha ganhos
🧮 Admin vê quem mais vendeu e quanto pagar