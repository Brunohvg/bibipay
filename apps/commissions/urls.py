from django.urls import path
from .views import CommissionTrackingView, CommissionHistoryView

app_name = 'commissions'

urlpatterns = [
    path('', CommissionTrackingView.as_view(), name='commissions_tracking'),
    path('historico/', CommissionHistoryView.as_view(), name='commission_history'),
]