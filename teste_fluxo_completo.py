"""
Script de Teste - Fluxo Completo de Folha de Pagamento
Executa todos os passos do ciclo mensal

Uso: python teste_fluxo_completo.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from datetime import date
from django.db import transaction

from folha.services import FolhaService
from folha.models import FolhaPagamento, EventoPagamento, ItemFolha
from funcionarios.models import Funcionario, Adiantamento
from core.models import ProventoDesconto


def limpar_dados_teste(mes: int, ano: int):
    """Remove dados de teste anteriores"""
    print("\n" + "="*60)
    print("LIMPANDO DADOS DE TESTE ANTERIORES")
    print("="*60)
    
    # Remove folha e todos os dados relacionados
    folhas = FolhaPagamento.objects.filter(mes=mes, ano=ano)
    count = folhas.count()
    folhas.delete()
    
    # Remove adiantamentos do período
    Adiantamento.objects.all().update(status='P')  # Reset status
    
    print(f"   Folhas removidas: {count}")
    print("   Adiantamentos resetados para 'Pendente'")


def passo_1_abrir_competencia(mes: int, ano: int) -> FolhaPagamento:
    """PASSO 1: Abrir competência"""
    print("\n" + "="*60)
    print(f"PASSO 1: ABRIR COMPETÊNCIA {mes:02d}/{ano}")
    print("="*60)
    
    folha = FolhaService.gerar_folha(mes=mes, ano=ano)
    
    print(f"\n✅ Folha criada: {folha}")
    print(f"   Status: {folha.get_status_display()}")
    print(f"   Contratos ativos: {folha.contratos_ativos.count()}")
    print(f"\n   Eventos criados:")
    for evento in folha.eventos.all():
        print(f"     - {evento.tipo_evento}: {evento.descricao}")
    
    print(f"\n💰 Totais iniciais:")
    print(f"   Proventos: R$ {folha.total_proventos:,.2f}")
    print(f"   Descontos: R$ {folha.total_descontos:,.2f}")
    print(f"   Líquido:   R$ {folha.total_liquido:,.2f}")
    
    return folha


def passo_2_adiantamento_massivo(folha: FolhaPagamento, dia: int, percentual: Decimal) -> EventoPagamento:
    """PASSO 2: Lançar adiantamento massivo"""
    print("\n" + "="*60)
    print(f"PASSO 2: ADIANTAMENTO MASSIVO ({percentual}% do salário)")
    print("="*60)
    
    data_adiantamento = date(folha.ano, folha.mes, dia)
    
    evento = FolhaService.criar_evento_adiantamento_massivo(
        folha=folha,
        descricao=f'Adiantamento Quinzenal {dia:02d}/{folha.mes:02d}',
        data_evento=data_adiantamento,
        percentual=percentual
    )
    
    print(f"\n✅ Evento de Adiantamento criado!")
    print(f"   Tipo: {evento.get_tipo_evento_display()}")
    print(f"   Data: {evento.data_evento}")
    print(f"   Valor Total: R$ {evento.valor_total:,.2f}")
    
    print(f"\n📋 Adiantamentos por funcionário:")
    for ad in Adiantamento.objects.filter(data_adiantamento=data_adiantamento):
        print(f"   - {ad.funcionario.nome_completo}: R$ {ad.valor} ({ad.get_status_display()})")
    
    return evento


def passo_3_processar_descontos(folha: FolhaPagamento):
    """PASSO 3: Processar descontos de adiantamento na folha"""
    print("\n" + "="*60)
    print("PASSO 3: PROCESSAR DESCONTOS DE ADIANTAMENTO")
    print("="*60)
    
    evento_pf = folha.eventos.get(tipo_evento='PF')
    
    # Buscar rubrica de desconto
    desconto_ad, _ = ProventoDesconto.objects.get_or_create(
        codigo_referencia='ADIANTAMENTO',
        defaults={
            'nome': 'Adiantamento Salarial',
            'tipo': 'D',
            'impacto': 'F'
        }
    )
    
    count = 0
    for adiantamento in Adiantamento.objects.filter(status='P'):
        # Criar item de desconto com rastreabilidade
        ItemFolha.objects.create(
            folha_pagamento=folha,
            evento_pagamento=evento_pf,
            funcionario=adiantamento.funcionario,
            provento_desconto=desconto_ad,
            valor_lancado=adiantamento.valor,
            justificativa=f'Adiantamento de {adiantamento.data_adiantamento}',
            adiantamento_origem=adiantamento
        )
        
        # Marcar como descontado
        adiantamento.status = 'D'
        adiantamento.save()
        
        print(f"   ✅ {adiantamento.funcionario.nome_completo}: -R$ {adiantamento.valor}")
        count += 1
    
    # Recalcular totais
    evento_pf.calcular_valor_total()
    
    print(f"\n   Total processado: {count} adiantamentos")
    print(f"\n💰 Folha atualizada:")
    print(f"   Proventos: R$ {folha.total_proventos:,.2f}")
    print(f"   Descontos: R$ {folha.total_descontos:,.2f}")
    print(f"   Líquido:   R$ {folha.total_liquido:,.2f}")


def passo_4_lancamento_manual(folha: FolhaPagamento, cpf: str = None):
    """PASSO 4: Lançamento manual (horas extras, etc.)"""
    print("\n" + "="*60)
    print("PASSO 4: LANÇAMENTOS MANUAIS (Exemplo: Horas Extras)")
    print("="*60)
    
    # Se não informou CPF, pega o primeiro funcionário
    if cpf:
        funcionario = Funcionario.objects.get(cpf=cpf)
    else:
        funcionario = folha.contratos_ativos.first().funcionario
    
    # Buscar ou criar provento de horas extras
    prov_he, _ = ProventoDesconto.objects.get_or_create(
        codigo_referencia='HORAS_EXTRAS',
        defaults={
            'nome': 'Horas Extras',
            'tipo': 'P',
            'impacto': 'F'
        }
    )
    
    evento_pf = folha.eventos.get(tipo_evento='PF')
    valor_he = Decimal('350.00')
    
    item = FolhaService.adicionar_item_manual(
        evento=evento_pf,
        funcionario=funcionario,
        provento_desconto=prov_he,
        valor=valor_he,
        justificativa='20 horas extras'
    )
    
    print(f"\n   ✅ Lançamento adicionado:")
    print(f"      Funcionário: {funcionario.nome_completo}")
    print(f"      Provento: {prov_he.nome}")
    print(f"      Valor: R$ {valor_he}")
    
    print(f"\n💰 Folha atualizada:")
    print(f"   Proventos: R$ {folha.total_proventos:,.2f}")
    print(f"   Descontos: R$ {folha.total_descontos:,.2f}")
    print(f"   Líquido:   R$ {folha.total_liquido:,.2f}")


def passo_5_fechar_folha(folha: FolhaPagamento):
    """PASSO 5: Fechar a folha"""
    print("\n" + "="*60)
    print("PASSO 5: FECHAR FOLHA")
    print("="*60)
    
    print(f"\n   Status antes: {folha.get_status_display()}")
    
    folha.fechar_folha()
    
    print(f"   Status depois: {folha.get_status_display()}")
    print(f"   Data fechamento: {folha.data_fechamento}")


def passo_6_processar_pagamento(folha: FolhaPagamento):
    """PASSO 6: Processar pagamentos"""
    print("\n" + "="*60)
    print("PASSO 6: PROCESSAR PAGAMENTOS")
    print("="*60)
    
    for evento in folha.eventos.all():
        print(f"\n   📄 {evento.descricao}")
        
        # Fechar evento se necessário
        if evento.status == 'R':
            evento.fechar_evento()
        
        # Marcar como pago
        evento.marcar_como_pago(data_pagamento=date.today())
        
        print(f"      Status: {evento.get_status_display()}")
        print(f"      Data pagamento: {evento.data_pagamento}")
        print(f"      Valor: R$ {evento.valor_total:,.2f}")
    
    # Marcar folha como paga
    folha.refresh_from_db()
    folha.marcar_como_paga()
    
    print(f"\n   ✅ Folha marcada como PAGA")


def imprimir_relatorio_final(folha: FolhaPagamento):
    """Imprime relatório final"""
    print("\n" + "="*60)
    print("RELATÓRIO FINAL")
    print("="*60)
    
    print(f"\n📊 FOLHA {folha.periodo_referencia}")
    print(f"   Status: {folha.get_status_display()}")
    print(f"   Fechada em: {folha.data_fechamento}")
    
    print(f"\n💰 TOTAIS:")
    print(f"   Proventos: R$ {folha.total_proventos:,.2f}")
    print(f"   Descontos: R$ {folha.total_descontos:,.2f}")
    print(f"   Líquido:   R$ {folha.total_liquido:,.2f}")
    
    print(f"\n📋 EVENTOS:")
    for evento in folha.eventos.all():
        print(f"   - {evento.get_tipo_evento_display()}: {evento.descricao}")
        print(f"     Status: {evento.get_status_display()} | Valor: R$ {evento.valor_total:,.2f}")
    
    print(f"\n👥 POR FUNCIONÁRIO:")
    funcionarios = {}
    for item in ItemFolha.objects.filter(folha_pagamento=folha):
        nome = item.funcionario.nome_completo
        if nome not in funcionarios:
            funcionarios[nome] = {'proventos': Decimal('0'), 'descontos': Decimal('0')}
        
        if item.provento_desconto.tipo == 'P':
            funcionarios[nome]['proventos'] += item.valor_lancado
        else:
            funcionarios[nome]['descontos'] += item.valor_lancado
    
    for nome, valores in funcionarios.items():
        liquido = valores['proventos'] - valores['descontos']
        print(f"   {nome}")
        print(f"      Proventos: R$ {valores['proventos']:,.2f}")
        print(f"      Descontos: R$ {valores['descontos']:,.2f}")
        print(f"      Líquido:   R$ {liquido:,.2f}")
    
    print(f"\n🔗 RASTREABILIDADE DE ADIANTAMENTOS:")
    for item in ItemFolha.objects.filter(folha_pagamento=folha, adiantamento_origem__isnull=False):
        print(f"   ItemFolha #{item.pk} → Adiantamento #{item.adiantamento_origem.pk}")
        print(f"      {item.funcionario.nome_completo}: R$ {item.valor_lancado}")


def executar_fluxo_completo(mes: int = 12, ano: int = 2024):
    """Executa o fluxo completo de folha de pagamento"""
    print("\n" + "#"*60)
    print("# TESTE DE FLUXO COMPLETO - FOLHA DE PAGAMENTO")
    print("#"*60)
    
    with transaction.atomic():
        # Limpar dados anteriores
        limpar_dados_teste(mes, ano)
        
        # Passo 1: Abrir competência
        folha = passo_1_abrir_competencia(mes, ano)
        
        # Passo 2: Adiantamento massivo (40%)
        passo_2_adiantamento_massivo(folha, dia=15, percentual=Decimal('40.00'))
        
        # Passo 3: Processar descontos
        passo_3_processar_descontos(folha)
        
        # Passo 4: Lançamento manual
        passo_4_lancamento_manual(folha)
        
        # Passo 5: Fechar folha
        passo_5_fechar_folha(folha)
        
        # Passo 6: Processar pagamento
        passo_6_processar_pagamento(folha)
        
        # Relatório final
        imprimir_relatorio_final(folha)
    
    print("\n" + "#"*60)
    print("# TESTE CONCLUÍDO COM SUCESSO! ✅")
    print("#"*60 + "\n")


if __name__ == '__main__':
    # Parâmetros padrão: Dezembro/2024
    mes = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    ano = int(sys.argv[2]) if len(sys.argv) > 2 else 2024
    
    executar_fluxo_completo(mes, ano)
