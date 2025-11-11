from django.urls import path
from .views import (
    dashboard_redirect_view,
    AdminDashboardView,
    SellerDashboardView,
    # BoxDashboardView,
)

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_redirect_view, name='dashboard_redirect'),
    path('admin/', AdminDashboardView.as_view(), name='dashboard_admin'),
    path('sellers/', SellerDashboardView.as_view(), name='dashboard_sellers'),
    # path('boxs/', BoxDashboardView.as_view(), name='dashboard_boxs'),
]
