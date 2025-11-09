from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from apps.core.models import BaseModel


class Commission(BaseModel):
    """
    Representa a comissão gerada a partir de uma venda (Sale).
    Cada venda pode ter apenas uma comissão (relação OneToOne).
    """

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'sellers'},
        help_text="Vendedor responsável pela venda."
    )
    sale = models.OneToOneField(
        'sales.Sale',
        on_delete=models.CASCADE,
        help_text="Venda associada à comissão."
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
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

    def calculate_value(self):
        """
        Calcula o valor da comissão com base na venda e na taxa do vendedor.
        Evita erros se algum campo estiver vazio.
        """
        sale_amount = getattr(self.sale, 'total_amount', None)
        commission_rate = getattr(self.seller, 'commission_rate', None)

        if sale_amount is not None and commission_rate is not None:
            self.value = (Decimal(sale_amount) * Decimal(commission_rate)) / Decimal('100')
        else:
            self.value = Decimal('0.00')

        return self.value

    def set_percentage(self):
        """
        Define automaticamente o percentual de comissão do vendedor.
        """
        if hasattr(self.seller, 'commission_rate') and self.seller.commission_rate is not None:
            self.percentage = self.seller.commission_rate
        else:
            self.percentage = Decimal('0.00')
        return self.percentage

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para garantir que:
        - A porcentagem venha do vendedor.
        - O valor da comissão seja recalculado antes de salvar.
        - A data de pagamento seja registrada automaticamente.
        """
        self.set_percentage()
        self.calculate_value()

        if self.paid and not self.paid_at:
            self.paid_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comissão de {self.seller.first_name} - {self.sale.date}"
