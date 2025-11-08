## 🧩 Aliases Django + UV

Esses aliases facilitam o uso dos principais comandos do Django quando executados com o `uv`.

### 📄 Como configurar
Adicione as linhas abaixo no seu arquivo `~/.bashrc` (ou `~/.zshrc` se usar zsh), depois recarregue o terminal com:
```bash
source ~/.bashrc

# Inicia o servidor de desenvolvimento
alias run="uv run manage.py runserver"

# Aplica migrações no banco de dados
alias mig="uv run manage.py migrate"

# Cria novas migrações a partir das alterações nos models
alias makemig="uv run manage.py makemigrations"

# Cria um novo superusuário
alias su="uv run manage.py createsuperuser"

# Abre o shell interativo do Django
alias sh="uv run manage.py shell"

run
mig
makemig
su
sh