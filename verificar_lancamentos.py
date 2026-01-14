"""
Script para verificar lançamentos fixos dos funcionários
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from funcionarios.models import Funcionario, LancamentoFixo, Contrato
from core.models import LancamentoFixoGeral
from folha.models import FolhaPagamento, ItemFolha
from datetime import date

print("\n" + "="*80)
print("DIAGNÓSTICO - LANÇAMENTOS FIXOS")
print("="*80)

# 1. Lançamentos Fixos Gerais
print("\n1. LANÇAMENTOS FIXOS GERAIS")
print("-"*80)
lancs_gerais = LancamentoFixoGeral.objects.filter(ativo=True)
print(f"Total: {lancs_gerais.count()}")
for lanc in lancs_gerais:
    valor_str = f"R$ {lanc.valor}" if lanc.valor else f"{lanc.percentual}%"
    print(f"  • {lanc.provento_desconto.nome}: {valor_str}")
    print(f"    Período: {lanc.data_inicio} até {lanc.data_fim or 'permanente'}")

# 2. Lançamentos Fixos por Funcionário
print("\n2. LANÇAMENTOS FIXOS POR FUNCIONÁRIO")
print("-"*80)
funcionarios = Funcionario.objects.all()
for func in funcionarios:
    lancs = func.lancamentos_fixos.all()
    contratos = func.contratos.count()
    
    print(f"\n{func.nome_completo}")
    print(f"  Contratos: {contratos}")
    print(f"  Lançamentos fixos: {lancs.count()}")
    
    if lancs.exists():
        for lanc in lancs:
            valor_str = f"R$ {lanc.valor}" if lanc.valor else f"{lanc.percentual}%"
            data_fim_str = lanc.data_fim.strftime('%d/%m/%Y') if lanc.data_fim else 'permanente'
            print(f"    - {lanc.provento_desconto.nome}: {valor_str}")
            print(f"      ({lanc.data_inicio.strftime('%d/%m/%Y')} até {data_fim_str})")

# 3. Última Folha Gerada
print("\n3. ÚLTIMA FOLHA DE PAGAMENTO")
print("-"*80)
ultima_folha = FolhaPagamento.objects.order_by('-ano', '-mes').first()
if ultima_folha:
    print(f"Folha: {ultima_folha.periodo_referencia}")
    print(f"Status: {ultima_folha.get_status_display()}")
    
    # Verifica itens da folha
    itens = ItemFolha.objects.filter(folha_pagamento=ultima_folha).select_related(
        'funcionario', 'provento_desconto'
    )
    
    print(f"\nItens na folha: {itens.count()}")
    
    # Agrupa por funcionário
    funcionarios_na_folha = {}
    for item in itens:
        func_nome = item.funcionario.nome_completo
        if func_nome not in funcionarios_na_folha:
            funcionarios_na_folha[func_nome] = []
        funcionarios_na_folha[func_nome].append(item)
    
    print(f"Funcionários processados: {len(funcionarios_na_folha)}")
    
    for func_nome, itens_func in funcionarios_na_folha.items():
        print(f"\n  {func_nome}:")
        for item in itens_func:
            print(f"    • {item.provento_desconto.nome}: R$ {item.valor_lancado}")
            if item.justificativa:
                print(f"      ({item.justificativa})")
else:
    print("Nenhuma folha de pagamento cadastrada")

print("\n" + "="*80)
print("DIAGNÓSTICO COMPLETO")
print("="*80 + "\n")
