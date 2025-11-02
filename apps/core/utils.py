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


"""from django.urls import reverse_lazy

APP_MAPPING = {
    'admin': 'admin',
    'sellers': 'accounts',
    'boxs': 'boxs',
}

def redirect_user_by_type(user):
    
    Retorna a URL de redirecionamento baseada no tipo do usuário.
    Cria automaticamente o nome da URL: <app_name>:<user_type>_dashboard
    
    app_name = APP_MAPPING.get(user.user_type)
    if app_name:
        url_name = f"{user.user_type}_dashboard"
        return reverse_lazy(f"{app_name}:{url_name}")
    
    return reverse_lazy('default_dashboard')
"""