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
from .models import LancamentoFixoGeral
from .forms import LancamentoFixoGeralForm


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
