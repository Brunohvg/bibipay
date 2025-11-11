from django.shortcuts import redirect


def dashboard_redirect_view(request):
    """Redireciona o usuário para o dashboard correto conforme o tipo."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    user_type = getattr(request.user, 'user_type', None)

    match user_type:
        case 'admin':
            return redirect('dashboard:dashboard_admin')
        case 'sellers':
            return redirect('dashboard:dashboard_sellers')
        case 'boxs':
            return redirect('dashboard:dashboard_boxs')
        case _:
            return redirect('accounts:login')
