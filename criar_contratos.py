"""
Script para criar contratos para os funcionários existentes
Execute: python manage.py shell < criar_contratos.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from funcionarios.models import Funcionario, Contrato
from core.models import TipoContrato
from datetime import date

print("\n" + "="*80)
print("CRIANDO CONTRATOS PARA OS FUNCIONÁRIOS")
print("="*80)

# Busca ou cria o tipo de contrato CLT
tipo_contrato, created = TipoContrato.objects.get_or_create(
    nome='CLT',
    defaults={'descricao': 'Contrato CLT - Regime de Trabalho'}
)

if created:
    print(f"\n✓ Tipo de contrato 'CLT' criado")
else:
    print(f"\n✓ Usando tipo de contrato existente: {tipo_contrato.nome}")

# Busca funcionários sem contrato
funcionarios = Funcionario.objects.all()
contratos_criados = 0

print(f"\nProcessando {funcionarios.count()} funcionários...")

for funcionario in funcionarios:
    # Verifica se já tem contrato
    if funcionario.contratos.exists():
        print(f"  ⊘ {funcionario.nome_completo} - Já possui contrato")
        continue
    
    # Cria contrato a partir da data de admissão
    contrato = Contrato.objects.create(
        funcionario=funcionario,
        tipo_contrato=tipo_contrato,
        data_inicio=funcionario.data_admissao,
        data_fim=None,  # Sem data fim = ativo indefinidamente
        carga_horaria=44  # 44 horas semanais (padrão CLT)
    )
    
    print(f"  ✓ {funcionario.nome_completo} - Contrato criado (início: {contrato.data_inicio})")
    contratos_criados += 1

print("\n" + "="*80)
print(f"RESUMO: {contratos_criados} contrato(s) criado(s)")
print("="*80)

if contratos_criados > 0:
    print("\n✓ Agora você pode gerar a folha de pagamento novamente!")
    print("  Os funcionários aparecerão na folha.")
else:
    print("\n⚠️ Todos os funcionários já possuem contratos.")

print("\n")
