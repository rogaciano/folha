"""
Views do app Folha de Pagamento
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from .models import FolhaPagamento, EventoPagamento, ItemFolha, ResumoFolhaFuncionario
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
    """Detalhes da folha de pagamento com suporte a visualização consolidada ou por evento"""
    folha = get_object_or_404(FolhaPagamento, pk=pk)
    filtro_pagamento = request.GET.get('pagamento', 'todos')
    evento_id = request.GET.get('evento', 'consolidado')
    
    eventos = folha.get_eventos_pagamento()
    evento_selecionado = None
    resumo_evento_list = []

    if evento_id and evento_id != 'consolidado':
        try:
            evento_selecionado = folha.eventos.get(pk=int(evento_id))
        except (EventoPagamento.DoesNotExist, ValueError):
            evento_selecionado = None

    if evento_selecionado:
        from decimal import Decimal
        if evento_selecionado.tipo_evento == 'AD':
            # Evento de Adiantamento: busca diretamente da tabela de Adiantamentos
            from funcionarios.models import Adiantamento
            adiantamentos = Adiantamento.objects.filter(
                data_adiantamento__month=folha.mes,
                data_adiantamento__year=folha.ano
            ).select_related('funcionario').order_by('funcionario__nome_completo')

            for ad in adiantamentos:
                resumo_evento_list.append({
                    'funcionario': ad.funcionario,
                    'total_proventos': ad.valor,
                    'total_descontos': Decimal('0.00'),
                    'valor_liquido': ad.valor,
                    'pago': ad.pago,
                    'data_pagamento': ad.data_pagamento,
                    'itens': [],
                    'adiantamento_id': ad.pk,
                })
        else:
            # Demais eventos (Pagamento Final, 13º, Férias): agrupa itens do evento por funcionário
            itens_evento = evento_selecionado.itens.select_related('funcionario', 'provento_desconto').order_by('funcionario__nome_completo')
            from itertools import groupby

            for func, func_itens in groupby(itens_evento, key=lambda i: i.funcionario):
                itens_list = list(func_itens)
                proventos = sum((i.valor_lancado for i in itens_list if i.provento_desconto.tipo == 'P'), Decimal('0.00'))
                descontos = sum((i.valor_lancado for i in itens_list if i.provento_desconto.tipo == 'D'), Decimal('0.00'))
                liquido = proventos - descontos
                pago = len(itens_list) > 0 and all(i.pago for i in itens_list)
                data_pagamento = next((i.data_pagamento for i in itens_list if i.data_pagamento), None)

                resumo_evento_list.append({
                    'funcionario': func,
                    'total_proventos': proventos,
                    'total_descontos': descontos,
                    'valor_liquido': liquido,
                    'pago': pago,
                    'data_pagamento': data_pagamento,
                    'itens': itens_list,
                })

        total_funcionarios = len(resumo_evento_list)
        total_pagos = sum(1 for r in resumo_evento_list if r['pago'])
        total_pendentes = total_funcionarios - total_pagos

        if filtro_pagamento == 'pagos':
            resumo_evento_list = [r for r in resumo_evento_list if r['pago']]
        elif filtro_pagamento == 'pendentes':
            resumo_evento_list = [r for r in resumo_evento_list if not r['pago']]

        resumos = None
    else:
        # Visão Consolidada da Folha
        resumos = ResumoFolhaFuncionario.objects.filter(
            folha_pagamento=folha
        ).select_related('funcionario').order_by('funcionario__nome_completo')

        total_funcionarios = folha.resumos.count()
        total_pagos = folha.resumos.filter(pago=True).count()
        total_pendentes = total_funcionarios - total_pagos

        if filtro_pagamento == 'pagos':
            resumos = resumos.filter(pago=True)
        elif filtro_pagamento == 'pendentes':
            resumos = resumos.filter(pago=False)

    # Busca itens da folha para o detalhamento completo
    if evento_selecionado and evento_selecionado.tipo_evento != 'AD':
        itens = evento_selecionado.itens.select_related('funcionario', 'provento_desconto').order_by(
            'funcionario__nome_completo', 'provento_desconto__tipo', 'provento_desconto__nome'
        )
    else:
        itens = ItemFolha.objects.filter(
            folha_pagamento=folha
        ).select_related('funcionario', 'provento_desconto').order_by(
            'funcionario__nome_completo', 'provento_desconto__tipo', 'provento_desconto__nome'
        )
    
    context = {
        'folha': folha,
        'resumos': resumos,
        'resumo_evento_list': resumo_evento_list,
        'evento_selecionado': evento_selecionado,
        'evento_id': evento_id,
        'itens': itens,
        'eventos': eventos,
        'filtro_pagamento': filtro_pagamento,
        'total_funcionarios': total_funcionarios,
        'total_pagos': total_pagos,
        'total_pendentes': total_pendentes,
    }
    return render(request, 'folha/folha_detail.html', context)


@login_required
@require_POST
def evento_funcionario_toggle_pago(request, evento_pk, funcionario_pk):
    """Marca ou desmarca o pagamento de um funcionário em um evento específico"""
    from django.utils import timezone
    evento = get_object_or_404(EventoPagamento.objects.select_related('folha_pagamento'), pk=evento_pk)
    folha = evento.folha_pagamento
    from funcionarios.models import Funcionario, Adiantamento
    funcionario = get_object_or_404(Funcionario, pk=funcionario_pk)

    if evento.tipo_evento == 'AD':
        ad = Adiantamento.objects.filter(
            funcionario=funcionario,
            data_adiantamento__month=folha.mes,
            data_adiantamento__year=folha.ano
        ).first()

        if not ad:
            messages.error(request, 'Nenhum adiantamento encontrado para este funcionário nesta competência.')
            return redirect(f"{redirect('folha:detail', pk=folha.pk).url}?evento={evento.pk}")

        novo_status_pago = not ad.pago
        ad.pago = novo_status_pago
        ad.data_pagamento = timezone.now().date() if novo_status_pago else None
        ad.save(update_fields=['pago', 'data_pagamento'])

        # Verifica se todos os adiantamentos do mês foram pagos
        todos_ad_pagos = not Adiantamento.objects.filter(
            data_adiantamento__month=folha.mes,
            data_adiantamento__year=folha.ano,
            pago=False
        ).exists()

        if todos_ad_pagos:
            evento.status = 'P'
            evento.data_pagamento = timezone.now().date()
        else:
            if evento.status == 'P':
                evento.status = 'F'
                evento.data_pagamento = None
        evento.save(update_fields=['status', 'data_pagamento'])
    else:
        itens = ItemFolha.objects.filter(evento_pagamento=evento, funcionario=funcionario)
        if not itens.exists():
            messages.error(request, 'Nenhum lançamento encontrado para este funcionário no evento.')
            return redirect(f"{redirect('folha:detail', pk=folha.pk).url}?evento={evento.pk}")

        todos_pagos = all(i.pago for i in itens)
        novo_status_pago = not todos_pagos
        data_pagamento = timezone.now().date() if novo_status_pago else None

        # Atualiza todos os itens do funcionário no evento
        itens.update(pago=novo_status_pago, data_pagamento=data_pagamento)

        # Verifica se todos os itens do evento foram pagos para atualizar o status do evento
        todos_itens_evento_pagos = not evento.itens.filter(pago=False).exists()
        if todos_itens_evento_pagos:
            evento.status = 'P'
            evento.data_pagamento = timezone.now().date()
            evento.save(update_fields=['status', 'data_pagamento'])
        else:
            if evento.status == 'P':
                evento.status = 'F'
                evento.data_pagamento = None
                evento.save(update_fields=['status', 'data_pagamento'])

    # Sincroniza o status consolidado do funcionário na folha
    todos_itens_func_na_folha_pagos = not ItemFolha.objects.filter(folha_pagamento=folha, funcionario=funcionario, pago=False).exists()
    resumo_func = ResumoFolhaFuncionario.objects.filter(folha_pagamento=folha, funcionario=funcionario).first()
    if resumo_func:
        if todos_itens_func_na_folha_pagos:
            resumo_func.pago = True
            resumo_func.data_pagamento = timezone.now().date()
        else:
            resumo_func.pago = False
            resumo_func.data_pagamento = None
        resumo_func.save(update_fields=['pago', 'data_pagamento'])

    folha.sincronizar_pagamentos_individuais()

    if novo_status_pago:
        messages.success(request, f'Pagamento de {funcionario.nome_completo} em {evento.descricao} marcado como pago.')
    else:
        messages.success(request, f'Pagamento de {funcionario.nome_completo} em {evento.descricao} desmarcado.')

    filtro_pagamento = request.GET.get('pagamento') or request.POST.get('pagamento')
    query_params = f"?evento={evento.pk}"
    if filtro_pagamento in ['pagos', 'pendentes']:
        query_params += f"&pagamento={filtro_pagamento}"

    return redirect(f"{redirect('folha:detail', pk=folha.pk).url}{query_params}")


@login_required
@require_POST
def resumo_toggle_pago(request, pk):
    """Marca ou desmarca o pagamento consolidado de um funcionário na folha"""
    resumo = get_object_or_404(ResumoFolhaFuncionario.objects.select_related('folha_pagamento', 'funcionario'), pk=pk)
    folha = resumo.folha_pagamento

    if resumo.pago:
        resumo.desmarcar_pagamento()
        # Desmarca itens
        ItemFolha.objects.filter(folha_pagamento=folha, funcionario=resumo.funcionario).update(pago=False, data_pagamento=None)
        messages.success(request, f'Pagamento de {resumo.funcionario.nome_completo} desmarcado.')
    else:
        resumo.marcar_como_pago()
        # Marca itens
        from django.utils import timezone
        ItemFolha.objects.filter(folha_pagamento=folha, funcionario=resumo.funcionario).update(pago=True, data_pagamento=timezone.now().date())
        messages.success(request, f'Pagamento de {resumo.funcionario.nome_completo} marcado com sucesso.')

    filtro_pagamento = request.GET.get('pagamento') or request.POST.get('pagamento')
    if filtro_pagamento in ['pagos', 'pendentes']:
        return redirect(f"{redirect('folha:detail', pk=folha.pk).url}?pagamento={filtro_pagamento}")

    return redirect('folha:detail', pk=folha.pk)


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
    messages.error(request, 'Use a coluna Pago no resumo por funcionário. A folha será marcada como paga automaticamente quando todos estiverem pagos.')
    
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
    messages.error(request, 'O evento será marcado como pago automaticamente quando todos os funcionários da folha estiverem pagos.')
    return redirect('folha:detail', pk=evento.folha_pagamento.pk)


# ==================== EXPORTAÇÃO ====================

@login_required
def folha_export_pdf(request, pk):
    """Exportar relatório de pagamento / conferência para PDF"""
    from .exports import export_relatorio_pagamento_pdf
    folha = get_object_or_404(FolhaPagamento, pk=pk)
    evento_id = request.GET.get('evento')
    filtro_pagamento = request.GET.get('pagamento', 'todos')
    
    evento = None
    if evento_id and evento_id != 'consolidado':
        try:
            evento = folha.eventos.get(pk=int(evento_id))
        except (EventoPagamento.DoesNotExist, ValueError):
            evento = None
            
    return export_relatorio_pagamento_pdf(folha, evento=evento, filtro_pagamento=filtro_pagamento)


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
