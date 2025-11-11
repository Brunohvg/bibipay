# apps/accounts/services.py
"""
CAMADA DE SERVIÇO (Service Layer)

Este arquivo contém toda a LÓGICA DE NEGÓCIO para o app 'accounts'.
Qualquer ação, como buscar, criar, atualizar ou deletar um usuário,
deve ser feita através de uma função neste arquivo.

As views (views.py) NUNCA devem falar diretamente com o banco de dados.
Elas devem chamar estas funções.
"""

from django.shortcuts import get_object_or_404
from .models import User  # Importa o modelo de usuário

# ==========================
# FUNÇÕES DE LEITURA (Read)
# ==========================

def get_seller_by_id(user_id: int) -> User:
    """
    Busca um vendedor específico pelo seu ID.
    
    Garante que o usuário encontrado é do tipo 'sellers'.
    Se não encontrar, levanta um erro 404.

    Args:
        user_id (int): A Chave Primária (pk) do usuário a ser buscado.

    Returns:
        User: O objeto User do vendedor encontrado.

    Raises:
        Http404: Se nenhum usuário for encontrado com esse ID e tipo.
    """
    # Esta é a lógica de negócio que estava repetida em 3 views diferentes.
    # Agora, ela fica em um único lugar (princípio DRY: Don't Repeat Yourself).
    seller = get_object_or_404(User, pk=user_id, user_type='sellers')
    return seller


def get_all_sellers():
    """
    Busca todos os usuários que são do tipo 'sellers'.

    Returns:
        QuerySet<User>: Uma lista (QuerySet) de todos os vendedores,
                        ordenados por nome.
    """
    # Esta é a lógica de consulta principal para a lista de vendedores.
    return User.objects.filter(user_type='sellers').order_by('first_name', 'last_name')


# ==========================
# FUNÇÕES DE AÇÃO (Write)
# ==========================

def toggle_seller_status(user_id: int) -> User:
    """
    Ativa ou desativa um vendedor (inverte o campo 'is_active').

    Args:
        user_id (int): O ID do vendedor a ser modificado.

    Returns:
        User: O objeto User do vendedor com o status já atualizado.
    """
    # 1. Busca o vendedor usando nossa outra função de serviço.
    #    Isso garante que a regra (ser 'sellers') seja aplicada.
    seller = get_seller_by_id(user_id)
    
    # 2. Executa a regra de negócio (inverter o status)
    seller.is_active = not seller.is_active
    
    # 3. Salva a mudança no banco de dados
    #    'update_fields' é uma boa prática para salvar apenas o campo alterado.
    seller.save(update_fields=['is_active'])
    
    return seller
