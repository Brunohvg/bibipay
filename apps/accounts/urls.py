from django.urls import path
from .views import CustomLoginView, CustomLogoutView, SellersCreateView, SellersListView, SellersDetailView, SellersDestroyView, SellersUpdateView, SellersDeactivateView



app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('sellers/create/', SellersCreateView.as_view(), name='sellers_create'),
    path('sellers/', SellersListView.as_view(), name='sellers_list'),
    path('sellers/<int:pk>/', SellersDetailView.as_view(), name='sellers_detail'),
    path('sellers/<int:pk>/delete/', SellersDestroyView.as_view(), name='sellers_delete'),
    path('sellers/<int:pk>/update/', SellersUpdateView.as_view(), name='sellers_update'),
    path('sellers/<int:pk>/deactivate/', SellersDeactivateView.as_view(), name='sellers_deactivate'),

    # outras URLs como logout, reset de senha, etc.
]