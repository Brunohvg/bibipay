from django.urls import path
from .views import SaleCreateView, SaleListView

app_name = 'sales'

urlpatterns = [
    path('create/', SaleCreateView.as_view(), name='sales_create'),
    path('list/', SaleListView.as_view(), name='sales_list'),
    #path('dashboard/', sale_dashboard, name='sales_dashboard'),
]