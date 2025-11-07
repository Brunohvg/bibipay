from django.shortcuts import redirect

def redirect_by_user_type(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('login')

        path = request.path  # URL atual

        # Evita loop: só redireciona se estiver fora do painel certo
        if user.user_type == 'admin' and not path.startswith('/dashboard/admin/'):
            return redirect('dashboard:dashboard_admin')
        elif user.user_type == 'sellers' and not path.startswith('/dashboard/sellers/'):
            return redirect('dashboard:dashboard_sellers')
        elif user.user_type == 'boxs' and not path.startswith('/dashboard/boxs/'):
            return redirect('dashboard:dashboard_boxs')

        return view_func(request, *args, **kwargs)
    return wrapper
