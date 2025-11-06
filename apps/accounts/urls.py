from django.urls import path
from .views import CustomLoginView, CustomLogoutView, SellersCreateView, SellersListView, SellersDetailView, SellersDestroyView



app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('sellers/create/', SellersCreateView.as_view(), name='sellers_create'),
    path('sellers/', SellersListView.as_view(), name='sellers_list'),
    path('sellers/<int:pk>/', SellersDetailView.as_view(), name='sellers_detail'),
    path('sellers/<int:pk>/delete/', SellersDestroyView.as_view(), name='sellers_delete'),

    
    # outras URLs como logout, reset de senha, etc.
]