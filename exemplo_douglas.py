"""
Exemplo Prático: Gestão de Pagamento do Funcionário Douglas Alan

Cenário:
- Salário Base: R$ 2.600,00
- Adiantamento Quinzenal (15/01):
  * 50% do salário: R$ 1.300,00
  * Bônus: R$ 134,00
  * TOTAL PAGO: R$ 1.434,00

- Pagamento Final (30/01):
  * Saldo do salário: R$ 1.300,00 (50% restante)
  * Horas extras: (a definir)
  * Descontos: (INSS, IRRF, etc)
  * Desconto do adiantamento: -R$ 1.434,00
  * LÍQUIDO A PAGAR: Saldo + Extras - Descontos - Adiantamento
"""

import os
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from datetime import date
from decimal import Decimal
from django.db import transaction

from folha.services import FolhaService
from folha.models import FolhaPagamento, EventoPagamento, ItemFolha
from funcionarios.models import Funcionario
from core.models import ProventoDesconto


def criar_ou_buscar_proventos_descontos():
    """Cria ou busca os proventos e descontos necessários"""
    
    # Salário Base
    salario, _ = ProventoDesconto.objects.get_or_create(
        codigo_referencia='SALARIO',
        defaults={
            'nome': 'Salário Base',
            'tipo': 'P',
            'impacto': 'F'
        }
    )
    
    # Bônus
    bonus, _ = ProventoDesconto.objects.get_or_create(
        codigo_referencia='BONUS',
        defaults={
            'nome': 'Bônus',
            'tipo': 'P',
            'impacto': 'F'
        }
    )
    
    # Horas Extras
    horas_extras, _ = ProventoDesconto.objects.get_or_create(
        codigo_referencia='HORAS_EXTRAS',
        defaults={
            'nome': 'Horas Extras',
            'tipo': 'P',
            'impacto': 'F'
        }
    )
    
    # Desconto de Adiantamento
    desc_adiantamento, _ = ProventoDesconto.objects.get_or_create(
        codigo_referencia='DESC_ADIANTAMENTO',
        defaults={
            'nome': 'Desconto Adiantamento Quinzenal',
            'tipo': 'D',
            'impacto': 'F'
        }
    )
    
    # INSS
    inss, _ = ProventoDesconto.objects.get_or_create(
        codigo_referencia='INSS',
        defaults={
            'nome': 'INSS',
            'tipo': 'D',
            'impacto': 'P'
        }
    )
    
    return {
        'salario': salario,
        'bonus': bonus,
        'horas_extras': horas_extras,
        'desc_adiantamento': desc_adiantamento,
        'inss': inss
    }


def exemplo_douglas_alan():
    """
    Simula o cenário completo do Douglas Alan
    """
    
    print("=" * 80)
    print("EXEMPLO PRÁTICO: DOUGLAS ALAN")
    print("=" * 80)
    print()
    
    # Busca o funcionário Douglas Alan
    try:
        douglas = Funcionario.objects.get(nome_completo__icontains='Douglas Alan')
        print(f"✓ Funcionário encontrado: {douglas.nome_completo}")
        print(f"  Salário Base: R$ {douglas.salario_base:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    except Funcionario.DoesNotExist:
        print("✗ Funcionário Douglas Alan não encontrado!")
        print("  Crie o funcionário primeiro no sistema.")
        return
    
    print()
    
    # Busca ou cria proventos/descontos
    proventos = criar_ou_buscar_proventos_descontos()
    print("✓ Proventos e Descontos configurados")
    print()
    
    # Dados do exemplo
    mes = 1
    ano = 2025
    salario_base = douglas.salario_base
    percentual_adiantamento = Decimal('0.50')  # 50%
    valor_bonus = Decimal('134.00')
    valor_horas_extras = Decimal('250.00')  # Exemplo
    
    with transaction.atomic():
        # 1. CRIA A FOLHA DE PAGAMENTO (COMPETÊNCIA)
        print("-" * 80)
        print("1. CRIANDO FOLHA DE PAGAMENTO (COMPETÊNCIA)")
        print("-" * 80)
        
        # Remove folha existente se houver (apenas para exemplo)
        FolhaPagamento.objects.filter(mes=mes, ano=ano).delete()
        
        folha = FolhaService.gerar_folha(
            mes=mes, 
            ano=ano, 
            criar_evento_padrao=False  # Não cria evento padrão
        )
        
        print(f"✓ Folha criada: {folha.periodo_referencia}")
        print(f"  Status: {folha.get_status_display()}")
        print()
        
        # 2. CRIA EVENTO DE ADIANTAMENTO QUINZENAL (DIA 15)
        print("-" * 80)
        print("2. EVENTO: ADIANTAMENTO QUINZENAL (15/01)")
        print("-" * 80)
        
        evento_adiantamento = FolhaService.criar_evento_pagamento(
            folha=folha,
            tipo_evento='AD',
            descricao='Adiantamento Quinzenal 15/01/2025',
            data_evento=date(ano, mes, 15),
            processar_funcionarios=False  # Não processa automaticamente
        )
        
        print(f"✓ Evento criado: {evento_adiantamento.descricao}")
        print()
        
        # 2.1. Lança 50% do salário
        valor_50_porcento = salario_base * percentual_adiantamento
        
        FolhaService.adicionar_item_manual(
            evento=evento_adiantamento,
            funcionario=douglas,
            provento_desconto=proventos['salario'],
            valor=valor_50_porcento,
            justificativa='Adiantamento quinzenal - 50% do salário'
        )
        
        print(f"  + Salário (50%): R$ {valor_50_porcento:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # 2.2. Lança o bônus
        FolhaService.adicionar_item_manual(
            evento=evento_adiantamento,
            funcionario=douglas,
            provento_desconto=proventos['bonus'],
            valor=valor_bonus,
            justificativa='Bônus quinzenal'
        )
        
        print(f"  + Bônus: R$ {valor_bonus:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # Recalcula totais
        evento_adiantamento.calcular_valor_total()
        
        print()
        print(f"  TOTAL PROVENTOS: R$ {evento_adiantamento.total_proventos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  TOTAL DESCONTOS: R$ {evento_adiantamento.total_descontos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  LÍQUIDO PAGO (15/01): R$ {evento_adiantamento.total_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print()
        
        # Marca como pago
        evento_adiantamento.marcar_como_pago(data_pagamento=date(ano, mes, 15))
        print(f"✓ Evento marcado como PAGO em {evento_adiantamento.data_pagamento}")
        print()
        
        # 3. CRIA EVENTO DE PAGAMENTO FINAL (DIA 30)
        print("-" * 80)
        print("3. EVENTO: PAGAMENTO FINAL (30/01)")
        print("-" * 80)
        
        evento_final = FolhaService.criar_evento_pagamento(
            folha=folha,
            tipo_evento='PF',
            descricao='Pagamento Final 30/01/2025',
            data_evento=date(ano, mes, 30),
            processar_funcionarios=False  # Controle manual
        )
        
        print(f"✓ Evento criado: {evento_final.descricao}")
        print()
        
        # 3.1. Lança os 50% restantes do salário
        valor_saldo_salario = salario_base * percentual_adiantamento
        
        FolhaService.adicionar_item_manual(
            evento=evento_final,
            funcionario=douglas,
            provento_desconto=proventos['salario'],
            valor=valor_saldo_salario,
            justificativa='Saldo do salário (50% restante)'
        )
        
        print(f"  + Saldo Salário (50%): R$ {valor_saldo_salario:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # 3.2. Lança horas extras
        FolhaService.adicionar_item_manual(
            evento=evento_final,
            funcionario=douglas,
            provento_desconto=proventos['horas_extras'],
            valor=valor_horas_extras,
            justificativa='Horas extras do mês'
        )
        
        print(f"  + Horas Extras: R$ {valor_horas_extras:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # 3.3. Calcula e lança INSS (exemplo simplificado - 9% sobre o total)
        base_inss = salario_base + valor_horas_extras
        valor_inss = base_inss * Decimal('0.09')
        
        FolhaService.adicionar_item_manual(
            evento=evento_final,
            funcionario=douglas,
            provento_desconto=proventos['inss'],
            valor=valor_inss,
            justificativa='INSS 9% sobre base de cálculo'
        )
        
        print(f"  - INSS (9%): R$ {valor_inss:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # 3.4. IMPORTANTE: Lança o desconto do adiantamento já pago
        valor_adiantamento_pago = evento_adiantamento.total_liquido
        
        FolhaService.adicionar_item_manual(
            evento=evento_final,
            funcionario=douglas,
            provento_desconto=proventos['desc_adiantamento'],
            valor=valor_adiantamento_pago,
            justificativa=f'Desconto do adiantamento pago em {evento_adiantamento.data_pagamento}'
        )
        
        print(f"  - Desconto Adiantamento: R$ {valor_adiantamento_pago:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # Recalcula totais
        evento_final.calcular_valor_total()
        
        print()
        print(f"  TOTAL PROVENTOS: R$ {evento_final.total_proventos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  TOTAL DESCONTOS: R$ {evento_final.total_descontos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  LÍQUIDO A PAGAR (30/01): R$ {evento_final.total_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print()
        
        # 4. RESUMO CONSOLIDADO
        print("=" * 80)
        print("4. RESUMO CONSOLIDADO DA COMPETÊNCIA")
        print("=" * 80)
        print()
        
        # Total de proventos da competência
        total_proventos_competencia = evento_adiantamento.total_proventos + evento_final.total_proventos
        
        # Total de descontos da competência (sem contar o desconto do adiantamento)
        total_descontos_competencia = evento_final.total_descontos - valor_adiantamento_pago
        
        # Total líquido da competência
        total_liquido_competencia = total_proventos_competencia - total_descontos_competencia
        
        # Total já pago
        total_ja_pago = evento_adiantamento.total_liquido
        
        # Total a pagar
        total_a_pagar = evento_final.total_liquido
        
        print(f"Competência: {folha.periodo_referencia}")
        print(f"Funcionário: {douglas.nome_completo}")
        print()
        print("PROVENTOS:")
        print(f"  Salário Base: R$ {salario_base:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  Bônus: R$ {valor_bonus:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  Horas Extras: R$ {valor_horas_extras:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  TOTAL PROVENTOS: R$ {total_proventos_competencia:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print()
        print("DESCONTOS:")
        print(f"  INSS: R$ {valor_inss:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  TOTAL DESCONTOS: R$ {total_descontos_competencia:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print()
        print(f"LÍQUIDO TOTAL: R$ {total_liquido_competencia:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print()
        print("PAGAMENTOS:")
        print(f"  ✓ Pago em 15/01 (Adiantamento): R$ {total_ja_pago:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print(f"  ⏳ A pagar em 30/01 (Final): R$ {total_a_pagar:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print()
        print(f"VERIFICAÇÃO: {total_ja_pago + total_a_pagar:,.2f} = {total_liquido_competencia:,.2f} ✓".replace(',', 'X').replace('.', ',').replace('X', '.'))
        print()
        
        # 5. DETALHAMENTO DOS EVENTOS
        print("=" * 80)
        print("5. DETALHAMENTO POR EVENTO")
        print("=" * 80)
        print()
        
        for evento in [evento_adiantamento, evento_final]:
            print(f"Evento: {evento.descricao}")
            print(f"Data: {evento.data_evento}")
            print(f"Status: {evento.get_status_display()}")
            print()
            
            itens = evento.itens.filter(funcionario=douglas).select_related('provento_desconto')
            
            for item in itens:
                tipo = "+" if item.provento_desconto.tipo == 'P' else "-"
                print(f"  {tipo} {item.provento_desconto.nome}: R$ {item.valor_lancado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                if item.justificativa:
                    print(f"    ({item.justificativa})")
            
            print()
            print(f"  Líquido: R$ {evento.total_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            print()
            print("-" * 80)
            print()
        
        print("=" * 80)
        print("EXEMPLO CONCLUÍDO COM SUCESSO!")
        print("=" * 80)


if __name__ == '__main__':
    exemplo_douglas_alan()
