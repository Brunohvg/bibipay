from turtle import up
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404
from apps.accounts.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from apps.core.utils import redirect_user_by_type
from apps.accounts.forms import SellersCreationForm, SellersUpdateForm
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return redirect_user_by_type(self.request.user)

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user:
            login(self.request, user)

            # Sessão expira ao fechar o navegador se não marcar "lembrar"
            if not self.request.POST.get('remember_me'):
                self.request.session.set_expiry(0)
                self.request.session.modified = True

            return super().form_valid(form)

        messages.error(self.request, "E-mail ou CPF e senha inválidos.", extra_tags='danger')
        return super().form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "E-mail ou CPF e senha inválidos.", extra_tags='danger')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = '/accounts/login/'


class SellersCreateView(CreateView):
    template_name = 'accounts/sellers_create.html'
    form_class = SellersCreationForm
    success_url = '/dashboard/admin'

    def form_valid(self, form):
        messages.success(self.request, "Conta criada com sucesso! Faça login para continuar.", extra_tags='success')
        return super().form_valid(form)


class SellersListView(ListView):
    model = User
    template_name = 'accounts/sellers_list.html'
    context_object_name = 'sellers'

    def get_queryset(self):
        return User.objects.filter(user_type='sellers').order_by('first_name', 'last_name')


class SellersDetailView(DetailView):
    model = User
    template_name = 'accounts/sellers_detail.html'
    context_object_name = 'seller'

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['pk'], user_type='sellers')   


class SellersUpdateView(UpdateView):
    model = User
    form_class = SellersUpdateForm
    template_name = 'accounts/sellers_update.html'
    context_object_name = 'seller'
    success_url = reverse_lazy('accounts:sellers_list')

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['pk'], user_type='sellers')


class SellersDestroyView(DeleteView):
    model = User
    template_name = 'accounts/sellers_confirm_delete.html'
    context_object_name = 'seller'
    success_url = reverse_lazy('accounts:sellers_list')

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['pk'], user_type='sellers')


from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from apps.accounts.models import User

class SellersDeactivateView(View):
    def get(self, request, pk, *args, **kwargs):
        seller = get_object_or_404(User, pk=pk, user_type='sellers')
        if seller.is_active:
            seller.is_active = False
            seller.save()   
            messages.success(request, f"Vendedor desativado com sucesso!", extra_tags='success')
        else:
            seller.is_active = True
            seller.save()
            messages.success(request, f"Vendedor ativado com sucesso!", extra_tags='success')
        return redirect(reverse_lazy('accounts:sellers_list'))
  
