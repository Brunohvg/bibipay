from django.urls import reverse

def redirect_user_by_type(user):
    """Retorna a URL de redirecionamento baseada no tipo do usuário."""
    mapping = {
        'admin': 'dashboard:dashboard',
        'sellers': 'dashboard:dashboard',
        'boxs': 'boxs_dashboard',
    }
    # Use reverse (não reverse_lazy) aqui, porque estamos no runtime da request
    return reverse(mapping.get(user.user_type, 'default_dashboard'))
