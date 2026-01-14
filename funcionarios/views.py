"""
Views do app Funcionários
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ValidationError

from .models import Funcionario, Contrato, LancamentoFixo, Adiantamento, Ferias
from .forms import (FuncionarioForm, ContratoForm, LancamentoFixoForm, AdiantamentoForm, 
                   AdiantamentoMassivoForm, FeriasForm)
from folha.services import AdiantamentoService


@login_required
def funcionario_list(request):
    """Lista de funcionários"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    
    funcionarios = Funcionario.objects.select_related('funcao', 'setor')
    
    if query:
        funcionarios = funcionarios.filter(
            Q(nome_completo__icontains=query) | Q(cpf__icontains=query)
        )
    
    if status:
        funcionarios = funcionarios.filter(status=status)
    else:
        funcionarios = funcionarios.filter(status='A')  # Default: apenas ativos
    
    funcionarios = funcionarios.order_by('nome_completo')
    
    context = {
        'funcionarios': funcionarios,
        'query': query,
        'status': status,
    }
    return render(request, 'funcionarios/funcionario_list.html', context)


@login_required
def funcionario_detail(request, pk):
    """Detalhes do funcionário"""
    funcionario = get_object_or_404(
        Funcionario.objects.select_related('funcao', 'setor'), 
        pk=pk
    )
    
    # Busca dados relacionados
    contratos = funcionario.contratos.all().order_by('-data_inicio')
    lancamentos_fixos = funcionario.lancamentos_fixos.all().order_by('-data_inicio')
    adiantamentos = funcionario.adiantamentos.all().order_by('-data_adiantamento')[:10]
    ferias = funcionario.ferias.all().order_by('-data_inicio_gozo')[:10]
    
    context = {
        'funcionario': funcionario,
        'contratos': contratos,
        'lancamentos_fixos': lancamentos_fixos,
        'adiantamentos': adiantamentos,
        'ferias': ferias,
    }
    return render(request, 'funcionarios/funcionario_detail.html', context)


@login_required
def funcionario_create(request):
    """Criar novo funcionário"""
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)
        if form.is_valid():
            funcionario = form.save()
            messages.success(request, f'Funcionário {funcionario.nome_completo} cadastrado com sucesso!')
            return redirect('funcionarios:detail', pk=funcionario.pk)
    else:
        form = FuncionarioForm()
    
    context = {'form': form, 'title': 'Novo Funcionário'}
    return render(request, 'funcionarios/funcionario_form.html', context)


@login_required
def funcionario_update(request, pk):
    """Editar funcionário"""
    funcionario = get_object_or_404(Funcionario, pk=pk)
    
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES, instance=funcionario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Funcionário {funcionario.nome_completo} atualizado com sucesso!')
            return redirect('funcionarios:detail', pk=funcionario.pk)
    else:
        form = FuncionarioForm(instance=funcionario)
    
    context = {'form': form, 'funcionario': funcionario, 'title': 'Editar Funcionário'}
    return render(request, 'funcionarios/funcionario_form.html', context)


@login_required
def adiantamento_massivo(request):
    """Lançamento massivo de itens na folha de pagamento"""
    if request.method == 'POST':
        form = AdiantamentoMassivoForm(request.POST)
        if form.is_valid():
            from folha.services import FolhaService
            from decimal import Decimal
            
            folha = form.cleaned_data['folha_pagamento']
            provento_desconto = form.cleaned_data['provento_desconto']
            
            # Verifica se a folha está em rascunho
            if folha.status != 'R':
                messages.error(request, 'Apenas folhas em rascunho podem receber lançamentos!')
                return render(request, 'funcionarios/adiantamento_massivo.html', {
                    'form': form, 
                    'title': 'Lançamento Massivo na Folha'
                })
            
            # Monta filtros de funcionários
            filtros = {}
            if form.cleaned_data.get('setor'):
                filtros['setor'] = form.cleaned_data['setor']
            if form.cleaned_data.get('funcao'):
                filtros['funcao'] = form.cleaned_data['funcao']
            if form.cleaned_data.get('status'):
                filtros['status'] = form.cleaned_data['status']
            else:
                filtros['status'] = 'A'  # Default: apenas ativos
            
            # Busca funcionários
            funcionarios = Funcionario.objects.filter(**filtros)
            
            # Determina valor
            tipo_valor = form.cleaned_data['tipo_valor']
            count = 0
            
            try:
                for funcionario in funcionarios:
                    # Calcula o valor
                    if tipo_valor == 'F':
                        valor = form.cleaned_data['valor_fixo']
                    else:  # Percentual
                        percentual = form.cleaned_data['percentual']
                        valor = (funcionario.salario_base * percentual) / Decimal('100')
                    
                    # Adiciona item na folha
                    justificativa = f'Lançamento massivo'
                    if form.cleaned_data.get('data_adiantamento'):
                        justificativa += f' - {form.cleaned_data["data_adiantamento"].strftime("%d/%m/%Y")}'
                    
                    FolhaService.adicionar_item_manual(
                        folha=folha,
                        funcionario=funcionario,
                        provento_desconto=provento_desconto,
                        valor=valor,
                        justificativa=justificativa
                    )
                    count += 1
                
                messages.success(
                    request, 
                    f'{count} lançamento(s) adicionado(s) à folha {folha.periodo_referencia}!'
                )
                return redirect('folha:detail', pk=folha.pk)
                
            except ValidationError as e:
                messages.error(request, f'Erro de validação: {str(e)}')
            except Exception as e:
                messages.error(request, f'Erro ao lançar: {str(e)}')
    else:
        form = AdiantamentoMassivoForm()
    
    context = {'form': form, 'title': 'Lançamento Massivo na Folha'}
    return render(request, 'funcionarios/adiantamento_massivo.html', context)


@login_required
def adiantamento_list(request):
    """Lista de adiantamentos"""
    status_filter = request.GET.get('status', '')
    mes_filter = request.GET.get('mes', '')
    ano_filter = request.GET.get('ano', '')
    
    adiantamentos = Adiantamento.objects.select_related('funcionario')
    
    if status_filter:
        adiantamentos = adiantamentos.filter(status=status_filter)
    
    if mes_filter:
        adiantamentos = adiantamentos.filter(data_adiantamento__month=mes_filter)
    
    if ano_filter:
        adiantamentos = adiantamentos.filter(data_adiantamento__year=ano_filter)
    
    adiantamentos = adiantamentos.order_by('-data_adiantamento')
    
    # Busca anos disponíveis para o filtro
    from django.db.models.functions import ExtractYear
    from datetime import datetime
    
    anos_disponiveis = Adiantamento.objects.annotate(
        ano=ExtractYear('data_adiantamento')
    ).values_list('ano', flat=True).distinct().order_by('-ano')
    
    # Se não houver anos nos adiantamentos, usa os últimos 3 anos incluindo o atual
    if not anos_disponiveis:
        ano_atual = datetime.now().year
        anos_disponiveis = [ano_atual, ano_atual - 1, ano_atual - 2]
    
    context = {
        'adiantamentos': adiantamentos,
        'status_filter': status_filter,
        'mes_filter': mes_filter,
        'ano_filter': ano_filter,
        'anos_disponiveis': anos_disponiveis,
    }
    return render(request, 'funcionarios/adiantamento_list.html', context)


# ==================== LANÇAMENTOS FIXOS ====================

@login_required
def lancamento_fixo_create(request, funcionario_pk):
    """Criar novo lançamento fixo"""
    funcionario = get_object_or_404(Funcionario, pk=funcionario_pk)
    
    if request.method == 'POST':
        form = LancamentoFixoForm(request.POST)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.funcionario = funcionario
            
            # Limpar o campo não utilizado baseado no tipo_valor
            tipo_valor = form.cleaned_data.get('tipo_valor')
            if tipo_valor == 'F':
                lancamento.percentual = None
            elif tipo_valor == 'P':
                lancamento.valor = None
            
            lancamento.save()
            messages.success(request, 'Lançamento fixo adicionado com sucesso!')
            return redirect('funcionarios:detail', pk=funcionario.pk)
    else:
        form = LancamentoFixoForm()
    
    # Buscar todos os proventos/descontos para o template
    from core.models import ProventoDesconto
    proventos_descontos = ProventoDesconto.objects.filter(ativo=True)
    
    context = {
        'form': form,
        'funcionario': funcionario,
        'proventos_descontos': proventos_descontos,
        'title': f'Novo Lançamento Fixo - {funcionario.nome_completo}'
    }
    return render(request, 'funcionarios/lancamento_fixo_form.html', context)


@login_required
def lancamento_fixo_update(request, pk):
    """Editar lançamento fixo"""
    lancamento = get_object_or_404(LancamentoFixo, pk=pk)
    
    if request.method == 'POST':
        form = LancamentoFixoForm(request.POST, instance=lancamento)
        if form.is_valid():
            lancamento_obj = form.save(commit=False)
            
            # Limpar o campo não utilizado baseado no tipo_valor
            tipo_valor = form.cleaned_data.get('tipo_valor')
            if tipo_valor == 'F':
                lancamento_obj.percentual = None
            elif tipo_valor == 'P':
                lancamento_obj.valor = None
            
            lancamento_obj.save()
            messages.success(request, 'Lançamento fixo atualizado com sucesso!')
            return redirect('funcionarios:detail', pk=lancamento.funcionario.pk)
    else:
        form = LancamentoFixoForm(instance=lancamento)
    
    # Buscar todos os proventos/descontos para o template
    from core.models import ProventoDesconto
    proventos_descontos = ProventoDesconto.objects.filter(ativo=True)
    
    context = {
        'form': form,
        'lancamento': lancamento,
        'funcionario': lancamento.funcionario,
        'proventos_descontos': proventos_descontos,
        'title': f'Editar Lançamento Fixo'
    }
    return render(request, 'funcionarios/lancamento_fixo_form.html', context)


@login_required
def lancamento_fixo_delete(request, pk):
    """Excluir lançamento fixo"""
    lancamento = get_object_or_404(LancamentoFixo, pk=pk)
    funcionario_pk = lancamento.funcionario.pk
    
    if request.method == 'POST':
        lancamento.delete()
        messages.success(request, 'Lançamento fixo removido com sucesso!')
    
    return redirect('funcionarios:detail', pk=funcionario_pk)


# ==================== FÉRIAS ====================

@login_required
def ferias_list(request):
    """Lista de férias"""
    status_filter = request.GET.get('status', '')
    
    ferias = Ferias.objects.select_related('funcionario').order_by('-data_inicio_gozo')
    
    if status_filter:
        ferias = ferias.filter(status=status_filter)
    
    context = {
        'ferias': ferias,
        'status_filter': status_filter,
    }
    return render(request, 'funcionarios/ferias_list.html', context)


@login_required
def ferias_create(request, funcionario_pk):
    """Criar novo registro de férias"""
    funcionario = get_object_or_404(Funcionario, pk=funcionario_pk)
    
    if request.method == 'POST':
        form = FeriasForm(request.POST)
        if form.is_valid():
            ferias = form.save(commit=False)
            ferias.funcionario = funcionario
            ferias.save()
            messages.success(request, 'Férias cadastradas com sucesso!')
            return redirect('funcionarios:detail', pk=funcionario.pk)
    else:
        # Calcula automaticamente o período aquisitivo
        periodo = Ferias.calcular_periodo_aquisitivo(funcionario.data_admissao)
        initial_data = {
            'periodo_inicio': periodo['inicio'],
            'periodo_fim': periodo['fim'],
        }
        form = FeriasForm(initial=initial_data)
    
    context = {
        'form': form,
        'funcionario': funcionario,
        'title': f'Cadastrar Férias - {funcionario.nome_completo}'
    }
    return render(request, 'funcionarios/ferias_form.html', context)


@login_required
def ferias_update(request, pk):
    """Editar registro de férias"""
    ferias = get_object_or_404(Ferias, pk=pk)
    
    if request.method == 'POST':
        form = FeriasForm(request.POST, instance=ferias)
        if form.is_valid():
            form.save()
            messages.success(request, 'Férias atualizadas com sucesso!')
            return redirect('funcionarios:detail', pk=ferias.funcionario.pk)
    else:
        form = FeriasForm(instance=ferias)
    
    context = {
        'form': form,
        'ferias': ferias,
        'funcionario': ferias.funcionario,
        'title': 'Editar Férias'
    }
    return render(request, 'funcionarios/ferias_form.html', context)


@login_required
def ferias_delete(request, pk):
    """Excluir registro de férias"""
    ferias = get_object_or_404(Ferias, pk=pk)
    funcionario_pk = ferias.funcionario.pk
    
    if request.method == 'POST':
        ferias.delete()
        messages.success(request, 'Férias removidas com sucesso!')
    
    return redirect('funcionarios:detail', pk=funcionario_pk)


@login_required
def organograma(request):
    """Visualização do organograma da empresa"""
    from core.models import Setor
    
    # Buscar funcionários sem superior (topo da hierarquia)
    funcionarios_topo = Funcionario.objects.filter(
        superior__isnull=True, 
        status='A'
    ).select_related('funcao', 'setor').prefetch_related('subordinados')
    
    # Buscar setores com seus chefes
    setores = Setor.objects.filter(ativo=True).select_related('chefe')
    
    context = {
        'funcionarios_topo': funcionarios_topo,
        'setores': setores,
        'total_funcionarios': Funcionario.objects.filter(status='A').count(),
    }
    
    return render(request, 'funcionarios/organograma.html', context)


@login_required
def contrato_create(request, funcionario_pk):
    """Criar novo contrato"""
    funcionario = get_object_or_404(Funcionario, pk=funcionario_pk)
    
    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.funcionario = funcionario
            try:
                contrato.save()  # O save() do modelo já chama full_clean()
                messages.success(request, 'Contrato cadastrado com sucesso!')
                return redirect('funcionarios:detail', pk=funcionario_pk)
            except ValidationError as e:
                messages.error(request, f'Erro de validação: {str(e)}')
            except Exception as e:
                messages.error(request, f'Erro ao salvar contrato: {str(e)}')
    else:
        form = ContratoForm()
    
    context = {
        'form': form,
        'funcionario': funcionario,
        'title': f'Novo Contrato - {funcionario.nome_completo}',
    }
    
    return render(request, 'funcionarios/contrato_form.html', context)


@login_required
def contrato_update(request, pk):
    """Editar contrato"""
    contrato = get_object_or_404(Contrato, pk=pk)
    
    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato)
        if form.is_valid():
            try:
                contrato_obj = form.save()  # O save() do modelo já chama full_clean()
                messages.success(request, 'Contrato atualizado com sucesso!')
                return redirect('funcionarios:detail', pk=contrato.funcionario.pk)
            except ValidationError as e:
                messages.error(request, f'Erro de validação: {str(e)}')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar contrato: {str(e)}')
    else:
        form = ContratoForm(instance=contrato)
    
    context = {
        'form': form,
        'contrato': contrato,
        'funcionario': contrato.funcionario,
        'title': f'Editar Contrato - {contrato.funcionario.nome_completo}',
    }
    
    return render(request, 'funcionarios/contrato_form.html', context)


@login_required
def contrato_delete(request, pk):
    """Excluir contrato"""
    contrato = get_object_or_404(Contrato, pk=pk)
    funcionario_pk = contrato.funcionario.pk
    
    if request.method == 'POST':
        contrato.delete()
        messages.success(request, 'Contrato removido com sucesso!')
    
    return redirect('funcionarios:detail', pk=funcionario_pk)
