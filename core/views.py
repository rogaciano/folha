"""
Views do app Core - Dashboard e páginas principais
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.contrib import messages
from datetime import date, timedelta

from funcionarios.models import Funcionario, Ferias
from folha.models import FolhaPagamento
from .models import LancamentoFixoGeral, Setor, Funcao, TipoContrato, ProventoDesconto
from .forms import (
    LancamentoFixoGeralForm, SetorForm, FuncaoForm,
    TipoContratoForm, ProventoDescontoForm
)


@login_required
def dashboard(request):
    """Dashboard principal do sistema"""
    
    # Estatísticas gerais
    total_funcionarios = Funcionario.objects.filter(status='A').count()
    total_inativos = Funcionario.objects.filter(status='I').count()
    total_ferias = Funcionario.objects.filter(status='F').count()
    
    # Total de salários dos funcionários ativos
    total_salarios = Funcionario.objects.filter(status='A').aggregate(
        total=Sum('salario_base')
    )['total'] or 0
    
    # Salário médio dos funcionários ativos
    salario_medio = total_salarios / total_funcionarios if total_funcionarios > 0 else 0
    
    # Projeção anual de salários
    projecao_anual = total_salarios * 12
    
    # Férias a vencer nos próximos 60 dias
    data_limite = date.today() + timedelta(days=60)
    ferias_a_vencer = Ferias.objects.filter(
        periodo_aquisitivo_fim__lte=data_limite,
        periodo_aquisitivo_fim__gte=date.today(),
        status='PR'
    ).select_related('funcionario')[:10]
    
    # Última folha de pagamento
    ultima_folha = FolhaPagamento.objects.order_by('-ano', '-mes').first()
    
    # Funcionários recém-admitidos (últimos 30 dias)
    data_limite_admissao = date.today() - timedelta(days=30)
    funcionarios_recentes = Funcionario.objects.filter(
        data_admissao__gte=data_limite_admissao,
        status='A'
    ).order_by('-data_admissao')[:5]
    
    context = {
        'total_funcionarios': total_funcionarios,
        'total_inativos': total_inativos,
        'total_ferias': total_ferias,
        'total_salarios': total_salarios,
        'salario_medio': salario_medio,
        'projecao_anual': projecao_anual,
        'ferias_a_vencer': ferias_a_vencer,
        'ultima_folha': ultima_folha,
        'funcionarios_recentes': funcionarios_recentes,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def lancamentos_fixos_gerais_list(request):
    """Lista todos os lançamentos fixos gerais"""
    lancamentos = LancamentoFixoGeral.objects.all().select_related('provento_desconto')
    
    context = {
        'lancamentos': lancamentos,
    }
    
    return render(request, 'core/lancamentos_fixos_gerais_list.html', context)


@login_required
def lancamentos_fixos_gerais_create(request):
    """Cria um novo lançamento fixo geral"""
    if request.method == 'POST':
        form = LancamentoFixoGeralForm(request.POST)
        if form.is_valid():
            lancamento = form.save()
            messages.success(request, 'Lançamento fixo geral criado com sucesso!')
            return redirect('core:lancamentos_fixos_gerais_list')
    else:
        form = LancamentoFixoGeralForm()
    
    context = {
        'form': form,
        'title': 'Novo Lançamento Fixo Geral',
        'button_text': 'Criar Lançamento'
    }
    
    return render(request, 'core/lancamentos_fixos_gerais_form.html', context)


@login_required
def lancamentos_fixos_gerais_update(request, pk):
    """Edita um lançamento fixo geral existente"""
    lancamento = get_object_or_404(LancamentoFixoGeral, pk=pk)
    
    if request.method == 'POST':
        form = LancamentoFixoGeralForm(request.POST, instance=lancamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lançamento fixo geral atualizado com sucesso!')
            return redirect('core:lancamentos_fixos_gerais_list')
    else:
        form = LancamentoFixoGeralForm(instance=lancamento)
    
    context = {
        'form': form,
        'lancamento': lancamento,
        'title': 'Editar Lançamento Fixo Geral',
        'button_text': 'Salvar Alterações'
    }
    
    return render(request, 'core/lancamentos_fixos_gerais_form.html', context)


@login_required
def lancamentos_fixos_gerais_delete(request, pk):
    """Exclui um lançamento fixo geral"""
    lancamento = get_object_or_404(LancamentoFixoGeral, pk=pk)
    
    if request.method == 'POST':
        lancamento.delete()
        messages.success(request, 'Lançamento fixo geral excluído com sucesso!')
        return redirect('core:lancamentos_fixos_gerais_list')
    
    context = {
        'lancamento': lancamento,
    }
    
    return render(request, 'core/lancamentos_fixos_gerais_delete.html', context)


# ==================== SETORES ====================

@login_required
def setor_list(request):
    """Lista todos os setores"""
    busca = request.GET.get('busca', '')
    status_filter = request.GET.get('status', '')
    
    setores = Setor.objects.all().select_related('chefe').annotate(
        total_funcionarios=Count('funcionarios', filter=Q(funcionarios__status='A'))
    )
    
    if busca:
        setores = setores.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
    if status_filter == 'ativo':
        setores = setores.filter(ativo=True)
    elif status_filter == 'inativo':
        setores = setores.filter(ativo=False)
        
    context = {
        'setores': setores,
        'busca': busca,
        'status_filter': status_filter,
    }
    return render(request, 'core/setor_list.html', context)


@login_required
def setor_create(request):
    """Criar novo setor"""
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor criado com sucesso!')
            return redirect('core:setor_list')
    else:
        form = SetorForm()
    
    context = {
        'form': form,
        'title': 'Novo Setor',
        'button_text': 'Criar Setor'
    }
    return render(request, 'core/setor_form.html', context)


@login_required
def setor_update(request, pk):
    """Editar setor existente"""
    setor = get_object_or_404(Setor, pk=pk)
    if request.method == 'POST':
        form = SetorForm(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor atualizado com sucesso!')
            return redirect('core:setor_list')
    else:
        form = SetorForm(instance=setor)
    
    context = {
        'form': form,
        'setor': setor,
        'title': f'Editar Setor: {setor.nome}',
        'button_text': 'Salvar Alterações'
    }
    return render(request, 'core/setor_form.html', context)


@login_required
def setor_delete(request, pk):
    """Excluir setor"""
    setor = get_object_or_404(Setor, pk=pk)
    if request.method == 'POST':
        # Se houver funcionários vinculados, avisa
        if setor.funcionarios.exists():
            messages.error(request, 'Não é possível excluir este setor pois existem colaboradores vinculados a ele. Considere desativá-lo.')
        else:
            setor.delete()
            messages.success(request, 'Setor excluído com sucesso!')
        return redirect('core:setor_list')
    
    context = {'objeto': setor, 'tipo': 'Setor', 'voltar_url': 'core:setor_list'}
    return render(request, 'core/confirm_delete.html', context)


# ==================== FUNÇÕES / CARGOS ====================

@login_required
def funcao_list(request):
    """Lista todas as funções/cargos"""
    busca = request.GET.get('busca', '')
    status_filter = request.GET.get('status', '')
    
    funcoes = Funcao.objects.all().annotate(
        total_funcionarios=Count('funcionarios', filter=Q(funcionarios__status='A'))
    )
    
    if busca:
        funcoes = funcoes.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
    if status_filter == 'ativo':
        funcoes = funcoes.filter(ativo=True)
    elif status_filter == 'inativo':
        funcoes = funcoes.filter(ativo=False)
        
    context = {
        'funcoes': funcoes,
        'busca': busca,
        'status_filter': status_filter,
    }
    return render(request, 'core/funcao_list.html', context)


@login_required
def funcao_create(request):
    """Criar nova função"""
    if request.method == 'POST':
        form = FuncaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Função/Cargo cadastrado com sucesso!')
            return redirect('core:funcao_list')
    else:
        form = FuncaoForm()
    
    context = {
        'form': form,
        'title': 'Nova Função / Cargo',
        'button_text': 'Cadastrar Cargo'
    }
    return render(request, 'core/funcao_form.html', context)


@login_required
def funcao_update(request, pk):
    """Editar função existente"""
    funcao = get_object_or_404(Funcao, pk=pk)
    if request.method == 'POST':
        form = FuncaoForm(request.POST, instance=funcao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Função/Cargo atualizado com sucesso!')
            return redirect('core:funcao_list')
    else:
        form = FuncaoForm(instance=funcao)
    
    context = {
        'form': form,
        'funcao': funcao,
        'title': f'Editar Função: {funcao.nome}',
        'button_text': 'Salvar Alterações'
    }
    return render(request, 'core/funcao_form.html', context)


@login_required
def funcao_delete(request, pk):
    """Excluir função"""
    funcao = get_object_or_404(Funcao, pk=pk)
    if request.method == 'POST':
        if funcao.funcionarios.exists():
            messages.error(request, 'Não é possível excluir esta função pois há colaboradores vinculados a ela. Considere desativá-la.')
        else:
            funcao.delete()
            messages.success(request, 'Função excluída com sucesso!')
        return redirect('core:funcao_list')
    
    context = {'objeto': funcao, 'tipo': 'Função / Cargo', 'voltar_url': 'core:funcao_list'}
    return render(request, 'core/confirm_delete.html', context)


# ==================== TIPOS DE CONTRATO ====================

@login_required
def tipo_contrato_list(request):
    """Lista todos os tipos de contrato"""
    busca = request.GET.get('busca', '')
    status_filter = request.GET.get('status', '')
    
    tipos = TipoContrato.objects.all().annotate(
        total_contratos=Count('contratos')
    )
    
    if busca:
        tipos = tipos.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
    if status_filter == 'ativo':
        tipos = tipos.filter(ativo=True)
    elif status_filter == 'inativo':
        tipos = tipos.filter(ativo=False)
        
    context = {
        'tipos': tipos,
        'busca': busca,
        'status_filter': status_filter,
    }
    return render(request, 'core/tipo_contrato_list.html', context)


@login_required
def tipo_contrato_create(request):
    """Criar novo tipo de contrato"""
    if request.method == 'POST':
        form = TipoContratoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de contrato cadastrado com sucesso!')
            return redirect('core:tipo_contrato_list')
    else:
        form = TipoContratoForm()
    
    context = {
        'form': form,
        'title': 'Novo Tipo de Contrato',
        'button_text': 'Cadastrar Tipo de Contrato'
    }
    return render(request, 'core/tipo_contrato_form.html', context)


@login_required
def tipo_contrato_update(request, pk):
    """Editar tipo de contrato"""
    tipo = get_object_or_404(TipoContrato, pk=pk)
    if request.method == 'POST':
        form = TipoContratoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de contrato atualizado com sucesso!')
            return redirect('core:tipo_contrato_list')
    else:
        form = TipoContratoForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'title': f'Editar Tipo de Contrato: {tipo.nome}',
        'button_text': 'Salvar Alterações'
    }
    return render(request, 'core/tipo_contrato_form.html', context)


@login_required
def tipo_contrato_delete(request, pk):
    """Excluir tipo de contrato"""
    tipo = get_object_or_404(TipoContrato, pk=pk)
    if request.method == 'POST':
        if tipo.contratos.exists():
            messages.error(request, 'Não é possível excluir este tipo de contrato pois há contratos registrados com ele. Considere desativá-lo.')
        else:
            tipo.delete()
            messages.success(request, 'Tipo de contrato excluído com sucesso!')
        return redirect('core:tipo_contrato_list')
    
    context = {'objeto': tipo, 'tipo': 'Tipo de Contrato', 'voltar_url': 'core:tipo_contrato_list'}
    return render(request, 'core/confirm_delete.html', context)


# ==================== PROVENTOS E DESCONTOS ====================

@login_required
def provento_desconto_list(request):
    """Lista todos os proventos e descontos"""
    busca = request.GET.get('busca', '')
    tipo_filter = request.GET.get('tipo', '')
    status_filter = request.GET.get('status', '')
    
    itens = ProventoDesconto.objects.all()
    
    if busca:
        itens = itens.filter(Q(nome__icontains=busca) | Q(codigo_referencia__icontains=busca) | Q(descricao__icontains=busca))
    if tipo_filter:
        itens = itens.filter(tipo=tipo_filter)
    if status_filter == 'ativo':
        itens = itens.filter(ativo=True)
    elif status_filter == 'inativo':
        itens = itens.filter(ativo=False)
        
    context = {
        'itens': itens,
        'busca': busca,
        'tipo_filter': tipo_filter,
        'status_filter': status_filter,
    }
    return render(request, 'core/provento_desconto_list.html', context)


@login_required
def provento_desconto_create(request):
    """Criar novo provento ou desconto"""
    if request.method == 'POST':
        form = ProventoDescontoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Provento/Desconto cadastrado com sucesso!')
            return redirect('core:provento_desconto_list')
    else:
        form = ProventoDescontoForm()
    
    context = {
        'form': form,
        'title': 'Novo Provento / Desconto',
        'button_text': 'Cadastrar Item'
    }
    return render(request, 'core/provento_desconto_form.html', context)


@login_required
def provento_desconto_update(request, pk):
    """Editar provento ou desconto"""
    item = get_object_or_404(ProventoDesconto, pk=pk)
    if request.method == 'POST':
        form = ProventoDescontoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Provento/Desconto atualizado com sucesso!')
            return redirect('core:provento_desconto_list')
    else:
        form = ProventoDescontoForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'title': f'Editar Item: {item.nome}',
        'button_text': 'Salvar Alterações'
    }
    return render(request, 'core/provento_desconto_form.html', context)


@login_required
def provento_desconto_delete(request, pk):
    """Excluir provento ou desconto"""
    item = get_object_or_404(ProventoDesconto, pk=pk)
    if request.method == 'POST':
        from folha.models import ItemFolha
        if ItemFolha.objects.filter(provento_desconto=item).exists():
            messages.error(request, 'Não é possível excluir este provento/desconto pois já existem folhas calculadas utilizando-o. Considere desativá-lo.')
        else:
            item.delete()
            messages.success(request, 'Item excluído com sucesso!')
        return redirect('core:provento_desconto_list')
    
    context = {'objeto': item, 'tipo': 'Provento / Desconto', 'voltar_url': 'core:provento_desconto_list'}
    return render(request, 'core/confirm_delete.html', context)
