from django.contrib import admin
from .models import Commission
@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('sale', 'percentage', 'value', 'paid', 'paid_at')
    list_filter = ('paid', 'sale__seller')
    search_fields = ('sale__seller__first_name', 'sale__seller__last_name', 'sale__id')
    readonly_fields = ('value', 'percentage'    )

    def save_model(self, request, obj, form, change):
        """
        Garante que o valor da comissão seja recalculado sempre que a comissão for salva.
        """
        obj.calculate_value()
        super().save_model(request, obj, form, change)
