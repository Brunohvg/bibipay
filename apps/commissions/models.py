from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from apps.core.models import BaseModel


class Commission(BaseModel):
    """
    Representa a comissão gerada a partir de uma venda (Sale).
    Cada venda possui apenas uma comissão.
    """

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'sellers'},
        related_name='commissions',
        help_text="Vendedor responsável pela venda."
    )
    sale = models.OneToOneField(
        'sales.Sale',
        on_delete=models.CASCADE,
        related_name='commission',
        help_text="Venda associada à comissão."
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Percentual de comissão aplicado ao vendedor."
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Valor final da comissão calculada."
    )
    paid = models.BooleanField(
        default=False,
        help_text="Indica se a comissão já foi paga."
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data e hora em que a comissão foi paga."
    )

    def set_percentage(self):
        """Define o percentual de comissão a partir do vendedor."""
        self.percentage = getattr(self.seller, 'commission_rate', Decimal('0.00')) or Decimal('0.00')

    def calculate_value(self):
        """Calcula o valor da comissão com base no valor da venda e na porcentagem."""
        sale_amount = getattr(self.sale, 'total_amount', Decimal('0.00'))
        self.value = (Decimal(sale_amount) * Decimal(self.percentage)) / Decimal('100')
        return self.value

    def save(self, *args, **kwargs):
        """
        - Garante que a porcentagem venha do vendedor.
        - Recalcula o valor antes de salvar.
        - Define data de pagamento, se necessário.
        """
        self.set_percentage()
        self.calculate_value()

        if self.paid and not self.paid_at:
            self.paid_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comissão de {self.seller.first_name} - {self.sale.date} - R$ {self.value:.2f}"
