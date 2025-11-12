from django.urls import path
from .views.auth import CustomLoginView, CustomLogoutView
from .views.sellers import SellersCreateView, SellersListView, SellersDetailView, SellersDestroyView, SellersUpdateView, SellersDeactivateView, SellerProfileUpdateView


app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('sellers/', SellersListView.as_view(), name='sellers_list'),
    path('sellers/create/', SellersCreateView.as_view(), name='sellers_create'),
    path('sellers/<int:pk>/', SellersDetailView.as_view(), name='sellers_detail'),
    path('sellers/<int:pk>/delete/', SellersDestroyView.as_view(), name='sellers_delete'),
    path('sellers/<int:pk>/update/', SellersUpdateView.as_view(), name='sellers_update'),
    path('sellers/<int:pk>/deactivate/', SellersDeactivateView.as_view(), name='sellers_deactivate'),
    path('profile/', SellerProfileUpdateView.as_view(), name='seller_profile'),

    # outras URLs como logout, reset de senha, etc.
]