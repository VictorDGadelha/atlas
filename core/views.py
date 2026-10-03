from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import RegistroPesoForm
from .models import RegistroPeso

@login_required
def home(request):
    return render(request, 'core/home.html')

@login_required
def peso(request):
    if request.method == 'POST':
        form = RegistroPesoForm(request.POST)
        if form.is_valid():
            # Se já existe registro nessa data, atualiza; senão, cria
            RegistroPeso.objects.update_or_create(
                usuario=request.user,
                data=form.cleaned_data['data'],
                defaults={'peso': form.cleaned_data['peso']},
            )
            messages.success(request, 'Peso salvo!')
            return redirect('peso')
    else:
        form = RegistroPesoForm(initial={'data': timezone.localdate()})

    registros = list(RegistroPeso.objects.filter(usuario=request.user))
    atual = registros[0] if registros else None
    variacao = None
    if len(registros) > 1:
        variacao = registros[0].peso - registros[1].peso

    return render(request, 'core/peso.html', {
        'form': form,
        'registros': registros,
        'atual': atual,
        'variacao': variacao,
    })


@login_required
@require_POST
def peso_excluir(request, pk):
    registro = get_object_or_404(RegistroPeso, pk=pk, usuario=request.user)
    registro.delete()
    messages.success(request, 'Registro excluído.')
    return redirect('peso')