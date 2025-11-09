from email import message
from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from .models import Sale
from .forms import SaleForm
from django.contrib import messages


class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sales_create.html'
    success_url = reverse_lazy('sales:sales_create')

    def form_valid(self, form):
        messages.success(self.request, "Venda criada com sucesso!", extra_tags='success')

        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors.as_data())
        messages.error(self.request, f"{form.errors}Erro ao criar a venda. Verifique os dados e tente novamente.", extra_tags='danger')
        return super().form_invalid(form)

class SaleListView(ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 10

    def get_queryset(self):
        return Sale.objects.select_related('seller').all().order_by('-date')
    
def sale_dashboard(request):
    sales = Sale.objects.select_related('seller').all().order_by('-date')[:10]
    context = {
        'sales': sales,
    }
    return render(request, 'sales/sale_dashboard.html', context)
