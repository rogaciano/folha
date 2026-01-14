"""
Teste de compatibilidade do método adicionar_item_manual
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from decimal import Decimal
from folha.services import FolhaService
from folha.models import FolhaPagamento
from funcionarios.models import Funcionario
from core.models import ProventoDesconto

print("=" * 80)
print("TESTE DE COMPATIBILIDADE - adicionar_item_manual()")
print("=" * 80)
print()

# Busca dados de teste
folha = FolhaPagamento.objects.first()
funcionario = Funcionario.objects.first()
provento = ProventoDesconto.objects.filter(tipo='P').first()

if not all([folha, funcionario, provento]):
    print("✗ Dados de teste não encontrados!")
    print(f"  Folha: {folha}")
    print(f"  Funcionário: {funcionario}")
    print(f"  Provento: {provento}")
    exit(1)

print(f"✓ Folha: {folha}")
print(f"✓ Funcionário: {funcionario.nome_completo}")
print(f"✓ Provento: {provento.nome}")
print()

# Testa compatibilidade com parâmetro 'folha'
print("Testando: FolhaService.adicionar_item_manual(folha=...)")
try:
    item = FolhaService.adicionar_item_manual(
        folha=folha,
        funcionario=funcionario,
        provento_desconto=provento,
        valor=Decimal('100.00'),
        justificativa='Teste de compatibilidade'
    )
    
    print(f"✓ Item criado com sucesso!")
    print(f"  ID: {item.id}")
    print(f"  Evento: {item.evento_pagamento}")
    print(f"  Valor: R$ {item.valor_lancado}")
    print()
    
    # Remove o item de teste
    item.delete()
    print("✓ Item de teste removido")
    
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TESTE CONCLUÍDO!")
print("=" * 80)
