from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AtividadeForm, RefeicaoForm, RegistroPesoForm
from .models import Atividade, AtividadeDia, Refeicao, RegistroPeso

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

def _dia_da_requisicao(request):
    """Lê ?data=AAAA-MM-DD; se faltar ou for inválida, usa hoje."""
    try:
        return date.fromisoformat(request.GET.get('data', ''))
    except ValueError:
        return timezone.localdate()


@login_required
def alimentacao(request):
    dia = _dia_da_requisicao(request)

    if request.method == 'POST':
        form = RefeicaoForm(request.POST)
        if form.is_valid():
            refeicao = form.save(commit=False)
            refeicao.usuario = request.user
            refeicao.save()
            messages.success(request, 'Refeição registrada!')
            return redirect(f"{request.path}?data={refeicao.data.isoformat()}")
    else:
        form = RefeicaoForm(initial={'data': dia})

    refeicoes = Refeicao.objects.filter(usuario=request.user, data=dia)
    total_calorias = refeicoes.aggregate(total=Sum('calorias'))['total'] or 0

    return render(request, 'core/alimentacao.html', {
        'form': form,
        'dia': dia,
        'dia_anterior': dia - timedelta(days=1),
        'dia_seguinte': dia + timedelta(days=1),
        'eh_hoje': dia == timezone.localdate(),
        'refeicoes': refeicoes,
        'total_calorias': total_calorias,
    })


@login_required
def refeicao_editar(request, pk):
    refeicao = get_object_or_404(Refeicao, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = RefeicaoForm(request.POST, instance=refeicao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Refeição atualizada!')
            return redirect(f"/alimentacao/?data={refeicao.data.isoformat()}")
    else:
        form = RefeicaoForm(instance=refeicao)
    return render(request, 'core/refeicao_form.html', {'form': form, 'refeicao': refeicao})


@login_required
@require_POST
def refeicao_excluir(request, pk):
    refeicao = get_object_or_404(Refeicao, pk=pk, usuario=request.user)
    data = refeicao.data
    refeicao.delete()
    messages.success(request, 'Refeição excluída.')
    return redirect(f"/alimentacao/?data={data.isoformat()}")

def _resumo_checklist(usuario, dia):
    itens = AtividadeDia.objects.filter(
        atividade__usuario=usuario, atividade__ativa=True, data=dia
    )
    total = itens.count()
    feitas = itens.filter(concluida=True).count()
    percentual = round(feitas * 100 / total) if total else 0
    return total, feitas, percentual


@login_required
def checklist(request):
    dia = _dia_da_requisicao(request)

    # Gera a lista do dia: cria a marcação das atividades que ainda não têm
    atividades = list(
        Atividade.objects.filter(
            usuario=request.user, ativa=True, criada_em__date__lte=dia
        )
    )
    existentes = set(
        AtividadeDia.objects.filter(atividade__in=atividades, data=dia)
        .values_list('atividade_id', flat=True)
    )
    AtividadeDia.objects.bulk_create(
        [AtividadeDia(atividade=a, data=dia) for a in atividades if a.id not in existentes],
        ignore_conflicts=True,
    )

    itens = (
        AtividadeDia.objects
        .filter(atividade__usuario=request.user, atividade__ativa=True, data=dia)
        .select_related('atividade')
        .order_by('atividade__nome')
    )
    total, feitas, percentual = _resumo_checklist(request.user, dia)

    return render(request, 'core/checklist.html', {
        'form': AtividadeForm(),
        'dia': dia,
        'dia_anterior': dia - timedelta(days=1),
        'dia_seguinte': dia + timedelta(days=1),
        'eh_hoje': dia == timezone.localdate(),
        'itens': itens,
        'total': total,
        'feitas': feitas,
        'percentual': percentual,
    })


@login_required
@require_POST
def atividade_criar(request):
    form = AtividadeForm(request.POST)
    if form.is_valid():
        atividade = form.save(commit=False)
        atividade.usuario = request.user
        atividade.save()
        messages.success(request, 'Atividade criada! Ela aparece a partir de hoje.')
    else:
        messages.error(request, 'Informe um nome válido para a atividade.')
    return redirect('checklist')


@login_required
@require_POST
def atividade_arquivar(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk, usuario=request.user)
    atividade.ativa = False
    atividade.save(update_fields=['ativa'])
    messages.success(request, 'Atividade arquivada. O histórico foi mantido.')
    return redirect('checklist')


@login_required
@require_POST
def checklist_marcar(request, pk):
    item = get_object_or_404(AtividadeDia, pk=pk, atividade__usuario=request.user)
    item.concluida = request.POST.get('concluida') == 'true'
    item.save(update_fields=['concluida'])
    total, feitas, percentual = _resumo_checklist(request.user, item.data)
    return JsonResponse({
        'concluida': item.concluida,
        'total': total,
        'feitas': feitas,
        'percentual': percentual,
    })