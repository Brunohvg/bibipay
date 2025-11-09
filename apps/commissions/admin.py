from django.contrib import admin
from .models import Commission
@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('seller', 'sale', 'percentage', 'value', 'paid', 'paid_at')
    list_filter = ('paid', 'seller')
    search_fields = ('seller__first_name', 'seller__last_name', 'sale__id')
    readonly_fields = ('value', 'percentage'    )

    def save_model(self, request, obj, form, change):
        """
        Garante que o valor da comissão seja recalculado sempre que a comissão for salva.
        """
        obj.calculate_value()
        super().save_model(request, obj, form, change)
