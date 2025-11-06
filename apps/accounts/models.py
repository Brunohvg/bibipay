import re
from tkinter import N
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from apps.core.models import BaseModel

USER_TYPE = (
    ('admin', 'Admin'),
    ('staff', 'Staff'),
    ('sellers', 'Sellers'),
)

cpf_validator = RegexValidator(r'^\d{11}$', 'CPF deve ter 11 números.')

class UserManager(BaseUserManager):
    def create_user(self, email=None, cpf=None, password=None, **extra_fields):
        if not email and not cpf:
            raise ValueError("Email ou CPF devem ser fornecidos.")

        if email:
            email = self.normalize_email(email)
            extra_fields.setdefault("email", email)

        if cpf:
            cpf = re.sub(r'\D', '', cpf)
            extra_fields.setdefault("cpf", cpf)

        first_name = extra_fields.get("first_name", "").strip().title()
        last_name = extra_fields.get("last_name", "").strip().title()
        extra_fields["first_name"] = first_name
        extra_fields["last_name"] = last_name

        if not password:
            raise ValueError("Usuário deve ter senha.")

        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, cpf=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(email=email, cpf=cpf, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    cpf = models.CharField(
        max_length=14,
        unique=True,
        db_index=True,
        #validators=[cpf_validator],
        blank=True,
        null=True
    )
    email = models.EmailField(unique=True, db_index=True, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE, default='sellers')
    commission_rate = models.DecimalField(
    verbose_name='Taxa de Comissão (%)',
    max_digits=5,
    decimal_places=2,
    default=None,
    blank=True,
    null=True,
    help_text='Porcentagem da comissão sobre o total de vendas'
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["cpf", "first_name"]

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = re.sub(r'\D', '', self.cpf)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.cpf

    def get_full_name(self):
        return " ".join(filter(None, [self.first_name, self.last_name]))

    def get_short_name(self):
        return self.first_name or (self.email.split("@")[0] if self.email else self.cpf)
