from django.urls import path
from .views import SaleCreateView, SaleListView, SaleDeleteView, SaleUpdateView

app_name = 'sales'

urlpatterns = [
    path('create/', SaleCreateView.as_view(), name='sales_create'),
    path('list/', SaleListView.as_view(), name='sales_list'),
    path('sale/<int:pk>/update/', SaleUpdateView.as_view(), name='sales_update'),
    path('sale/<int:pk>/delete/', SaleDeleteView.as_view(), name='sales_delete'),
    #path('dashboard/', sale_dashboard, name='sales_dashboard'),
]