import re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CPFOrEmailBackend(ModelBackend):
    """Permite login via CPF ou e-mail."""
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        username = username.strip().lower()

        try:
            if "@" in username:
                user = User.objects.get(email=username)
            else:
                cpf_clean = re.sub(r'\D', '', username)
                user = User.objects.get(cpf=cpf_clean)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
