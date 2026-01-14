"""
Script de diagnóstico para verificar por que a folha está vazia
Execute: python manage.py shell < diagnostico_folha.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import date
from funcionarios.models import Funcionario, Contrato, LancamentoFixo
from core.models import LancamentoFixoGeral
from django.db.models import Q

print("\n" + "="*80)
print("DIAGNÓSTICO DA FOLHA DE PAGAMENTO - NOVEMBRO/2025")
print("="*80)

# Período da folha
mes = 11
ano = 2025
primeiro_dia = date(ano, mes, 1)
ultimo_dia = date(ano, mes + 1, 1) if mes < 12 else date(ano + 1, 1, 1)

print(f"\nPeríodo da folha: {primeiro_dia} até {ultimo_dia}")

# 1. Verifica funcionários
print("\n" + "-"*80)
print("1. FUNCIONÁRIOS CADASTRADOS")
print("-"*80)
funcionarios = Funcionario.objects.all()
print(f"Total de funcionários: {funcionarios.count()}")
for func in funcionarios:
    print(f"  • {func.nome_completo} - Status: {func.get_status_display()} - Admissão: {func.data_admissao}")

# 2. Verifica contratos
print("\n" + "-"*80)
print("2. CONTRATOS CADASTRADOS")
print("-"*80)
contratos = Contrato.objects.all().select_related('funcionario', 'tipo_contrato')
print(f"Total de contratos: {contratos.count()}")
for contrato in contratos:
    print(f"  • {contrato.funcionario.nome_completo}")
    print(f"    - Tipo: {contrato.tipo_contrato.nome}")
    print(f"    - Início: {contrato.data_inicio}")
    print(f"    - Fim: {contrato.data_fim if contrato.data_fim else 'Sem data fim (ativo)'}")
    print(f"    - Está ativo para nov/2025? {contrato.esta_ativo}")

# 3. Verifica contratos ativos para o período da folha
print("\n" + "-"*80)
print("3. CONTRATOS ATIVOS PARA NOVEMBRO/2025")
print("-"*80)
contratos_ativos = Contrato.objects.filter(
    data_inicio__lte=ultimo_dia
).filter(
    Q(data_fim__isnull=True) | Q(data_fim__gte=primeiro_dia)
).select_related('funcionario', 'tipo_contrato')

print(f"Total de contratos ativos no período: {contratos_ativos.count()}")
if contratos_ativos.exists():
    for contrato in contratos_ativos:
        print(f"  ✓ {contrato.funcionario.nome_completo} - {contrato.tipo_contrato.nome}")
else:
    print("  ⚠️ NENHUM CONTRATO ATIVO ENCONTRADO!")
    print("\n  Possíveis causas:")
    print("  1. Os contratos têm data_fim anterior a novembro/2025")
    print("  2. Os contratos têm data_inicio posterior a novembro/2025")
    print("  3. Não há contratos cadastrados")

# 4. Verifica lançamentos fixos gerais
print("\n" + "-"*80)
print("4. LANÇAMENTOS FIXOS GERAIS")
print("-"*80)
lancamentos_gerais = LancamentoFixoGeral.objects.filter(
    ativo=True,
    data_inicio__lte=ultimo_dia
).filter(
    Q(data_fim__isnull=True) | Q(data_fim__gte=primeiro_dia)
).select_related('provento_desconto')

print(f"Total de lançamentos gerais ativos: {lancamentos_gerais.count()}")
for lanc in lancamentos_gerais:
    tipo_valor = f"R$ {lanc.valor}" if lanc.valor else f"{lanc.percentual}%"
    print(f"  • {lanc.provento_desconto.nome} - {tipo_valor}")
    print(f"    Período: {lanc.data_inicio} até {lanc.data_fim if lanc.data_fim else 'Permanente'}")

# 5. Verifica lançamentos fixos por funcionário
print("\n" + "-"*80)
print("5. LANÇAMENTOS FIXOS POR FUNCIONÁRIO")
print("-"*80)
for func in funcionarios:
    lancamentos_func = LancamentoFixo.objects.filter(
        funcionario=func,
        data_inicio__lte=ultimo_dia
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=primeiro_dia)
    ).select_related('provento_desconto')
    
    if lancamentos_func.exists():
        print(f"\n{func.nome_completo}:")
        for lanc in lancamentos_func:
            tipo_valor = f"R$ {lanc.valor}" if lanc.valor else f"{lanc.percentual}%"
            print(f"  • {lanc.provento_desconto.nome} - {tipo_valor}")
    else:
        print(f"\n{func.nome_completo}: Nenhum lançamento fixo")

print("\n" + "="*80)
print("CONCLUSÃO")
print("="*80)

if contratos_ativos.count() == 0:
    print("\n⚠️ PROBLEMA IDENTIFICADO: Não há contratos ativos para novembro/2025")
    print("\nSOLUÇÃO:")
    print("1. Verifique se os funcionários têm contratos cadastrados")
    print("2. Se houver contratos, ajuste as datas:")
    print("   - data_inicio: deve ser anterior ou igual a 01/12/2025")
    print("   - data_fim: deve ser posterior ou igual a 01/11/2025 (ou deixe em branco)")
    print("\n3. Para criar/editar contratos, acesse:")
    print("   http://localhost:8000/admin/funcionarios/contrato/")
else:
    print(f"\n✓ Tudo OK! {contratos_ativos.count()} contrato(s) ativo(s) encontrado(s)")
    print("  A folha deveria ter sido gerada com funcionários.")

print("\n" + "="*80 + "\n")
