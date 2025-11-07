# apps/dashboard/urls.py
from django.urls import path
from django.shortcuts import redirect
from .views import AdminDashboardView, SellerDashboardView, BoxDashboardView

app_name = 'dashboard'

def dashboard_redirect_view(request):
    user = request.user
    if user.user_type == 'admin':
        return redirect('dashboard:dashboard_admin')
    elif user.user_type == 'sellers':
        return redirect('dashboard:dashboard_sellers')
    elif user.user_type == 'boxs':
        return redirect('dashboard:dashboard_boxs')
    return redirect('login')

urlpatterns = [
    path('', dashboard_redirect_view, name='dashboard_redirect'),
    path('admin/', AdminDashboardView.as_view(), name='dashboard_admin'),
    path('sellers/', SellerDashboardView.as_view(), name='dashboard_sellers'),
    path('boxs/', BoxDashboardView.as_view(), name='dashboard_boxs'),
]
