"""
Views do app Folha de Pagamento
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import FolhaPagamento, ItemFolha, ResumoFolhaFuncionario
from .forms import GerarFolhaForm, ItemFolhaForm, EventoAdiantamentoForm, EventoDecimoTerceiroForm
from .services import FolhaService


@login_required
def folha_list(request):
    """Lista de folhas de pagamento"""
    folhas = FolhaPagamento.objects.all().order_by('-ano', '-mes')
    
    context = {
        'folhas': folhas,
    }
    return render(request, 'folha/folha_list.html', context)


@login_required
def folha_detail(request, pk):
    """Detalhes da folha de pagamento"""
    folha = get_object_or_404(FolhaPagamento, pk=pk)
    
    # Busca resumos por funcionário
    resumos = ResumoFolhaFuncionario.objects.filter(
        folha_pagamento=folha
    ).select_related('funcionario').order_by('funcionario__nome_completo')
    
    # Busca itens da folha agrupados por funcionário
    itens = ItemFolha.objects.filter(
        folha_pagamento=folha
    ).select_related('funcionario', 'provento_desconto').order_by(
        'funcionario__nome_completo', 'provento_desconto__tipo', 'provento_desconto__nome'
    )
    eventos = folha.get_eventos_pagamento()
    
    context = {
        'folha': folha,
        'resumos': resumos,
        'itens': itens,
        'eventos': eventos,
    }
    return render(request, 'folha/folha_detail.html', context)


@login_required
def folha_gerar(request):
    """Gerar nova folha de pagamento"""
    if request.method == 'POST':
        form = GerarFolhaForm(request.POST)
        if form.is_valid():
            mes = int(form.cleaned_data['mes'])
            ano = form.cleaned_data['ano']
            
            try:
                folha = FolhaService.gerar_folha(mes, ano)
                messages.success(
                    request, 
                    f'Folha de {folha.periodo_referencia} gerada com sucesso!'
                )
                return redirect('folha:detail', pk=folha.pk)
            except ValidationError as e:
                messages.error(request, f'Erro ao gerar folha: {str(e)}')
            except Exception as e:
                messages.error(request, f'Erro inesperado: {str(e)}')
    else:
        form = GerarFolhaForm()
    
    context = {'form': form, 'title': 'Gerar Nova Folha de Pagamento'}
    return render(request, 'folha/folha_gerar.html', context)


@login_required
def folha_fechar(request, pk):
    """Fechar folha de pagamento"""
    folha = get_object_or_404(FolhaPagamento, pk=pk)
    
    try:
        folha.fechar_folha()
        messages.success(request, f'Folha de {folha.periodo_referencia} fechada com sucesso!')
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('folha:detail', pk=folha.pk)


@login_required
def folha_reabrir(request, pk):
    """Reabrir folha de pagamento"""
    folha = get_object_or_404(FolhaPagamento, pk=pk)
    
    try:
        folha.reabrir_folha()
        messages.success(request, f'Folha de {folha.periodo_referencia} reaberta com sucesso!')
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('folha:detail', pk=folha.pk)


@login_required
def folha_marcar_paga(request, pk):
    """Marcar folha como paga"""
    folha = get_object_or_404(FolhaPagamento, pk=pk)
    
    try:
        folha.marcar_como_paga()
        messages.success(request, f'Folha de {folha.periodo_referencia} marcada como paga!')
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('folha:detail', pk=folha.pk)


@login_required
def item_adicionar(request, folha_pk):
    """Adicionar item manual à folha"""
    folha = get_object_or_404(FolhaPagamento, pk=folha_pk)
    
    if folha.status != 'R':
        messages.error(request, 'Apenas folhas em rascunho podem ser editadas')
        return redirect('folha:detail', pk=folha.pk)
    
    if request.method == 'POST':
        form = ItemFolhaForm(request.POST, folha=folha)
        if form.is_valid():
            try:
                FolhaService.adicionar_item_manual(
                    folha=folha,
                    funcionario=form.cleaned_data['funcionario'],
                    provento_desconto=form.cleaned_data['provento_desconto'],
                    valor=form.cleaned_data['valor_lancado'],
                    justificativa=form.cleaned_data['justificativa']
                )
                messages.success(request, 'Item adicionado com sucesso!')
                return redirect('folha:detail', pk=folha.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ItemFolhaForm(folha=folha)
    
    context = {
        'form': form,
        'folha': folha,
        'title': f'Adicionar Item - Folha {folha.periodo_referencia}'
    }
    return render(request, 'folha/item_form.html', context)


@login_required
def item_remover(request, pk):
    """Remover item da folha"""
    item = get_object_or_404(ItemFolha, pk=pk)
    folha = item.folha_pagamento
    
    if folha.status != 'R':
        messages.error(request, 'Apenas folhas em rascunho podem ser editadas')
        return redirect('folha:detail', pk=folha.pk)
    
    try:
        FolhaService.remover_item(item)
        messages.success(request, 'Item removido com sucesso!')
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('folha:detail', pk=folha.pk)


# ==================== EVENTOS ====================

@login_required
def evento_criar_adiantamento(request, folha_pk):
    folha = get_object_or_404(FolhaPagamento, pk=folha_pk)
    if folha.status != 'R':
        messages.error(request, 'Apenas folhas em rascunho podem receber eventos')
        return redirect('folha:detail', pk=folha.pk)

    if request.method == 'POST':
        form = EventoAdiantamentoForm(request.POST)
        if form.is_valid():
            data_evento = form.cleaned_data['data_evento']
            valor = form.cleaned_data.get('valor')
            percentual = form.cleaned_data.get('percentual')
            filtros = {}
            if form.cleaned_data.get('setor_id'):
                filtros['setor_id'] = form.cleaned_data['setor_id']
            if form.cleaned_data.get('funcao_id'):
                filtros['funcao_id'] = form.cleaned_data['funcao_id']
            if form.cleaned_data.get('status'):
                filtros['status'] = form.cleaned_data['status']

            try:
                evento = FolhaService.criar_evento_adiantamento_massivo(
                    folha=folha,
                    descricao=f"Adiantamento Quinzenal {data_evento.strftime('%d/%m')}",
                    data_evento=data_evento,
                    filtros=filtros,
                    valor=valor,
                    percentual=percentual,
                )
                messages.success(request, f'Evento criado: {evento.descricao} (Total R$ {evento.valor_total})')
                return redirect('folha:detail', pk=folha.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = EventoAdiantamentoForm()

    return render(request, 'folha/evento_adiantamento_form.html', {'form': form, 'folha': folha, 'title': 'Novo Adiantamento'})


@login_required
def evento_criar_decimo_terceiro(request, folha_pk):
    folha = get_object_or_404(FolhaPagamento, pk=folha_pk)
    if folha.status != 'R':
        messages.error(request, 'Apenas folhas em rascunho podem receber eventos')
        return redirect('folha:detail', pk=folha.pk)

    if request.method == 'POST':
        form = EventoDecimoTerceiroForm(request.POST)
        if form.is_valid():
            data_evento = form.cleaned_data['data_evento']
            parcela = int(form.cleaned_data['parcela'])
            try:
                evento = FolhaService.criar_evento_decimo_terceiro(
                    folha=folha,
                    descricao=f"13º Salário - {parcela}ª Parcela",
                    data_evento=data_evento,
                    parcela=parcela,
                )
                messages.success(request, f'Evento criado: {evento.descricao} (Total R$ {evento.valor_total})')
                return redirect('folha:detail', pk=folha.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = EventoDecimoTerceiroForm()

    return render(request, 'folha/evento_13_form.html', {'form': form, 'folha': folha, 'title': 'Novo 13º Salário'})


@login_required
def evento_fechar(request, pk):
    from .models import EventoPagamento
    evento = get_object_or_404(EventoPagamento, pk=pk)
    try:
        if evento.tipo_evento == 'PF':
            folha = evento.folha_pagamento
            for contrato in folha.contratos_ativos.all():
                FolhaService._lancar_adiantamentos(folha, evento, contrato.funcionario)
        evento.fechar_evento()
        messages.success(request, 'Evento fechado com sucesso!')
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect('folha:detail', pk=evento.folha_pagamento.pk)


@login_required
def evento_reabrir(request, pk):
    from .models import EventoPagamento
    evento = get_object_or_404(EventoPagamento, pk=pk)
    try:
        evento.reabrir_evento()
        messages.success(request, 'Evento reaberto com sucesso!')
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect('folha:detail', pk=evento.folha_pagamento.pk)


@login_required
def evento_marcar_pago(request, pk):
    from .models import EventoPagamento
    evento = get_object_or_404(EventoPagamento, pk=pk)
    try:
        evento.marcar_como_pago()
        messages.success(request, 'Evento marcado como pago!')
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect('folha:detail', pk=evento.folha_pagamento.pk)


# ==================== EXPORTAÇÃO ====================

@login_required
def folha_export_pdf(request, pk):
    """Exportar folha para PDF"""
    from .exports import export_folha_pdf
    folha = get_object_or_404(FolhaPagamento, pk=pk)
    return export_folha_pdf(folha)


@login_required
def folha_export_excel(request, pk):
    """Exportar folha para Excel"""
    from .exports import export_folha_excel
    folha = get_object_or_404(FolhaPagamento, pk=pk)
    return export_folha_excel(folha)


@login_required
def holerite_pdf(request, folha_pk, funcionario_pk):
    """Exportar holerite individual em PDF"""
    from .exports import export_holerite_pdf
    from funcionarios.models import Funcionario
    
    folha = get_object_or_404(FolhaPagamento, pk=folha_pk)
    funcionario = get_object_or_404(Funcionario, pk=funcionario_pk)
    
    return export_holerite_pdf(folha, funcionario)
