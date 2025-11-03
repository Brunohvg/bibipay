from django.urls import path
from .views import CustomLoginView, CustomLogoutView, SellersCreateView


app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('sellers/create/', SellersCreateView.as_view(), name='sellers_create'),
    
    # outras URLs como logout, reset de senha, etc.
]