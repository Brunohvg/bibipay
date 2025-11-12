from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import User

class SellersCreationForm(UserCreationForm):
    commission_rate = forms.DecimalField(
        label='Taxa de Comissão (%)',
        max_digits=5,
        decimal_places=2,
        initial=1.00,
        required=False,  # Pode ser nulo, caso seja admin
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg has-icon',
            'placeholder': 'Ex: 1.00 para 1%',
            'step': '0.01',
            'min': '0',
        }),
    )

    password1 = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg has-icon',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password',
        }),
    )

    password2 = forms.CharField(
        label='Confirmar Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg has-icon',
            'placeholder': 'Digite novamente a senha',
            'autocomplete': 'new-password',
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'cpf', 'commission_rate')  # <-- adicionado aqui
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

        for field_name in ['password1', 'password2']:
            self.fields[field_name].help_text = None

        self.fields['email'].error_messages = {
            'unique': 'Este e-mail já está cadastrado.',
            'invalid': 'Digite um e-mail válido.'
        }
        self.fields['cpf'].error_messages = {
            'invalid': 'Digite um CPF válido no formato 000.000.000-00.'
        }

        for field in self.fields.values():
            field.required = True

    def save(self, commit=True):
        """Salva o vendedor com a comissão configurada corretamente."""
        user = super().save(commit=False)
        commission_rate = self.cleaned_data.get('commission_rate')
        if commission_rate is not None:
            user.commission_rate = commission_rate
        if commit:
            user.save()
        return user

class SellersUpdateForm(forms.ModelForm):
    commission_rate = forms.DecimalField(
        label='Taxa de Comissão (%)',
        max_digits=5,
        decimal_places=2,
        required=False,  # Pode ser nulo, caso seja admin
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg has-icon',
            'placeholder': 'Ex: 1.00 para 1%',
            'step': '0.01',
            'min': '0',
        }),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'cpf', 'commission_rate')
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


class SellerProfileForm(forms.ModelForm):
    """
    Formulário para o vendedor editar o próprio perfil.
    """
    class Meta:
        model = User
        # Campos que o vendedor PODE editar:
        fields = ['first_name', 'last_name', 'email']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        # Garante que o email não seja alterado para um já existente
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este e-mail já está em uso por outra conta.")
        return email