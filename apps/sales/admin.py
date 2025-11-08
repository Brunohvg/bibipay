from django.contrib import admin
from .models import Sale
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'date', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('date', 'seller')
    search_fields = ('seller__username', 'seller__email')
    ordering = ('-date',)