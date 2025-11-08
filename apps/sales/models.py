from django.db import models
from apps.core.models import BaseModel
from django.conf import settings
from django.core.exceptions import ValidationError


class Sale(BaseModel):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'sellers'},
        related_name='sales'
    )
    date = models.DateField(db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['seller', 'date'], 
                name='unique_sale_per_seller_per_day'
            )
        ]

    def clean(self):
        if Sale.objects.filter(seller=self.seller, date=self.date).exclude(pk=self.pk).exists():
            raise ValidationError("Já existe uma venda registrada para este vendedor nesta data.")

    def __str__(self):
        return f"{self.seller.first_name} - {self.date.strftime('%d/%m/%Y')} - R$ {self.total_amount:.2f}"
