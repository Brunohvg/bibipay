from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from apps.core.models import BaseModel


class Commission(BaseModel):
    """
    Representa a comissão gerada a partir de uma venda (Sale).
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
        db_index=True, # 💡 OTIMIZAÇÃO: Para consultas mais rápidas de paid=False
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
        # Se for a primeira vez (criação), atribui o seller e a sale
        if not self.pk:
            # Garante que as FKs estejam preenchidas antes do cálculo
            if self.seller and self.sale:
                self.set_percentage()
                self.calculate_value()
        
        # O self.seller já deve ter sido definido antes de chamar save() se o modelo for criado via forms/views.

        if self.paid and not self.paid_at:
            self.paid_at = timezone.now()
        # Se paid for desmarcado, limpa o paid_at
        elif not self.paid and self.paid_at:
            self.paid_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        # Acesso ao sale.date só é seguro se a sale existir
        sale_date = self.sale.date.strftime('%d/%m/%Y') if self.sale and self.sale.date else 'Sem data'
        return f"Comissão de {self.seller.first_name} - {sale_date} - R$ {self.value:.2f}"