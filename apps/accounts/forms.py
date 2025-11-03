from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import User

class SellersCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg has-icon',
                'placeholder': 'Mínimo 8 caracteres',
                'autocomplete': 'new-password',
            }
        ),
    )

    password2 = forms.CharField(
        label='Confirmar Senha',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg has-icon',
                'placeholder': 'Digite novamente a senha',
                'autocomplete': 'new-password',
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'cpf')
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'cpf': 'CPF',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg has-icon',
                'placeholder': 'Ex: João'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg has-icon',
                'placeholder': 'Ex: Silva'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg has-icon',
                'placeholder': 'vendedor@exemplo.com'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control form-control-lg has-icon',
                'placeholder': '000.000.000-00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help texts padrão do UserCreationForm
        for field_name in ['password1', 'password2']:
            self.fields[field_name].help_text = None

        # Ajusta mensagens de erro amigáveis
        self.fields['email'].error_messages = {
            'unique': 'Este e-mail já está cadastrado.',
            'invalid': 'Digite um e-mail válido.'
        }
        self.fields['cpf'].error_messages = {
            'invalid': 'Digite um CPF válido no formato 000.000.000-00.'
        }

        # Marca todos os campos como obrigatórios
        for field in self.fields.values():
            field.required = True
