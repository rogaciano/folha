#!/usr/bin/env python
"""
Script para criar dados iniciais no sistema
Execute: python setup_initial_data.py
"""
import os
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.models import Setor, Funcao, TipoContrato, ProventoDesconto


def criar_setores():
    """Cria setores padrão"""
    setores = [
        {'nome': 'Tecnologia', 'descricao': 'Departamento de TI e Desenvolvimento'},
        {'nome': 'Recursos Humanos', 'descricao': 'Gestão de Pessoas e RH'},
        {'nome': 'Financeiro', 'descricao': 'Departamento Financeiro e Contábil'},
        {'nome': 'Comercial', 'descricao': 'Vendas e Atendimento ao Cliente'},
        {'nome': 'Operacional', 'descricao': 'Operações e Logística'},
        {'nome': 'Marketing', 'descricao': 'Marketing e Comunicação'},
        {'nome': 'Administrativo', 'descricao': 'Administração Geral'},
    ]
    
    print("Criando setores...")
    for setor_data in setores:
        setor, created = Setor.objects.get_or_create(
            nome=setor_data['nome'],
            defaults={'descricao': setor_data['descricao']}
        )
        if created:
            print(f"  ✓ Setor criado: {setor.nome}")
        else:
            print(f"  - Setor já existe: {setor.nome}")


def criar_funcoes():
    """Cria funções padrão"""
    funcoes = [
        {'nome': 'Desenvolvedor Jr', 'nivel_salarial_referencia': 3500.00},
        {'nome': 'Desenvolvedor Pleno', 'nivel_salarial_referencia': 6000.00},
        {'nome': 'Desenvolvedor Sênior', 'nivel_salarial_referencia': 10000.00},
        {'nome': 'Analista Jr', 'nivel_salarial_referencia': 3000.00},
        {'nome': 'Analista Pleno', 'nivel_salarial_referencia': 5000.00},
        {'nome': 'Analista Sênior', 'nivel_salarial_referencia': 8000.00},
        {'nome': 'Gerente', 'nivel_salarial_referencia': 12000.00},
        {'nome': 'Coordenador', 'nivel_salarial_referencia': 8000.00},
        {'nome': 'Assistente', 'nivel_salarial_referencia': 2500.00},
        {'nome': 'Auxiliar', 'nivel_salarial_referencia': 2000.00},
        {'nome': 'Estagiário', 'nivel_salarial_referencia': 1500.00},
    ]
    
    print("\nCriando funções...")
    for funcao_data in funcoes:
        funcao, created = Funcao.objects.get_or_create(
            nome=funcao_data['nome'],
            defaults={'nivel_salarial_referencia': funcao_data['nivel_salarial_referencia']}
        )
        if created:
            print(f"  ✓ Função criada: {funcao.nome}")
        else:
            print(f"  - Função já existe: {funcao.nome}")


def criar_tipos_contrato():
    """Cria tipos de contrato padrão"""
    tipos = [
        {'nome': 'CLT', 'descricao': 'Consolidação das Leis do Trabalho'},
        {'nome': 'Estágio', 'descricao': 'Contrato de Estágio'},
        {'nome': 'PJ', 'descricao': 'Pessoa Jurídica'},
        {'nome': 'Temporário', 'descricao': 'Contrato Temporário'},
        {'nome': 'Autônomo', 'descricao': 'Profissional Autônomo'},
    ]
    
    print("\nCriando tipos de contrato...")
    for tipo_data in tipos:
        tipo, created = TipoContrato.objects.get_or_create(
            nome=tipo_data['nome'],
            defaults={'descricao': tipo_data['descricao']}
        )
        if created:
            print(f"  ✓ Tipo de contrato criado: {tipo.nome}")
        else:
            print(f"  - Tipo de contrato já existe: {tipo.nome}")


def criar_proventos_descontos():
    """Cria proventos e descontos padrão"""
    items = [
        # Proventos
        {
            'nome': 'Salário Base',
            'codigo_referencia': 'SALARIO',
            'tipo': 'P',
            'impacto': 'F',
            'descricao': 'Salário base do funcionário'
        },
        {
            'nome': 'Vale Transporte',
            'codigo_referencia': 'VT',
            'tipo': 'P',
            'impacto': 'F',
            'descricao': 'Vale transporte'
        },
        {
            'nome': 'Vale Alimentação',
            'codigo_referencia': 'VA',
            'tipo': 'P',
            'impacto': 'F',
            'descricao': 'Vale alimentação ou refeição'
        },
        {
            'nome': 'Hora Extra 50%',
            'codigo_referencia': 'HE50',
            'tipo': 'P',
            'impacto': 'F',
            'descricao': 'Hora extra com adicional de 50%'
        },
        {
            'nome': 'Hora Extra 100%',
            'codigo_referencia': 'HE100',
            'tipo': 'P',
            'impacto': 'F',
            'descricao': 'Hora extra com adicional de 100%'
        },
        {
            'nome': 'Comissão',
            'codigo_referencia': 'COMISSAO',
            'tipo': 'P',
            'impacto': 'F',
            'descricao': 'Comissão sobre vendas'
        },
        {
            'nome': 'Bonificação',
            'codigo_referencia': 'BONUS',
            'tipo': 'P',
            'impacto': 'P',
            'descricao': 'Bonificação percentual'
        },
        {
            'nome': 'Adicional Noturno',
            'codigo_referencia': 'ANOTURN',
            'tipo': 'P',
            'impacto': 'P',
            'descricao': 'Adicional para trabalho noturno'
        },
        # Descontos
        {
            'nome': 'INSS',
            'codigo_referencia': 'INSS',
            'tipo': 'D',
            'impacto': 'P',
            'descricao': 'Desconto do INSS'
        },
        {
            'nome': 'IRRF',
            'codigo_referencia': 'IRRF',
            'tipo': 'D',
            'impacto': 'P',
            'descricao': 'Imposto de Renda Retido na Fonte'
        },
        {
            'nome': 'Adiantamento Salarial',
            'codigo_referencia': 'ADIANTAMENTO',
            'tipo': 'D',
            'impacto': 'F',
            'descricao': 'Desconto de adiantamento'
        },
        {
            'nome': 'Desconto Vale Transporte',
            'codigo_referencia': 'DVALE',
            'tipo': 'D',
            'impacto': 'P',
            'descricao': 'Desconto do vale transporte (6% do salário)'
        },
        {
            'nome': 'Falta Injustificada',
            'codigo_referencia': 'FALTA',
            'tipo': 'D',
            'impacto': 'F',
            'descricao': 'Desconto por falta injustificada'
        },
        {
            'nome': 'Pensão Alimentícia',
            'codigo_referencia': 'PENSAO',
            'tipo': 'D',
            'impacto': 'P',
            'descricao': 'Pensão alimentícia'
        },
        {
            'nome': 'Empréstimo Consignado',
            'codigo_referencia': 'EMPREST',
            'tipo': 'D',
            'impacto': 'F',
            'descricao': 'Parcela de empréstimo consignado'
        },
    ]
    
    print("\nCriando proventos e descontos...")
    for item_data in items:
        item, created = ProventoDesconto.objects.get_or_create(
            codigo_referencia=item_data['codigo_referencia'],
            defaults={
                'nome': item_data['nome'],
                'tipo': item_data['tipo'],
                'impacto': item_data['impacto'],
                'descricao': item_data['descricao']
            }
        )
        if created:
            tipo_str = "Provento" if item.tipo == 'P' else "Desconto"
            print(f"  ✓ {tipo_str} criado: {item.nome}")
        else:
            print(f"  - Item já existe: {item.nome}")


def main():
    """Executa todas as funções de criação de dados"""
    print("="*60)
    print("SETUP DE DADOS INICIAIS - Sistema de Folha de Pagamento")
    print("="*60)
    
    try:
        criar_setores()
        criar_funcoes()
        criar_tipos_contrato()
        criar_proventos_descontos()
        
        print("\n" + "="*60)
        print("✓ SETUP CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("\nPróximos passos:")
        print("1. Execute: python manage.py runserver")
        print("2. Acesse: http://localhost:8000/admin")
        print("3. Faça login com seu superusuário")
        print("4. Comece a cadastrar funcionários!")
        
    except Exception as e:
        print(f"\n✗ ERRO: {str(e)}")
        print("\nCertifique-se de que:")
        print("1. As migrações foram executadas: python manage.py migrate")
        print("2. Você está no diretório correto do projeto")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
