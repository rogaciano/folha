"""
Script para configurar hierarquia básica
Execute: python setup_hierarquia.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from funcionarios.models import Funcionario
from core.models import Setor

def setup_hierarquia():
    """Configura hierarquia básica"""
    
    print("="*60)
    print("CONFIGURAÇÃO DE HIERARQUIA")
    print("="*60)
    
    # Listar setores e funcionários
    print("\n📋 SETORES DISPONÍVEIS:")
    print("-" * 60)
    setores = Setor.objects.filter(ativo=True)
    
    if not setores.exists():
        print("❌ Nenhum setor cadastrado!")
        print("   Cadastre setores primeiro no Admin: /admin/core/setor/")
        return
    
    for setor in setores:
        print(f"\n🏢 Setor: {setor.nome}")
        print(f"   ID: {setor.id}")
        
        if setor.chefe:
            print(f"   ✅ Chefe atual: {setor.chefe.nome_completo}")
        else:
            print(f"   ⚠️  SEM CHEFE DEFINIDO")
        
        funcionarios = setor.funcionarios.filter(status='A')
        print(f"   👥 Funcionários: {funcionarios.count()}")
        
        for func in funcionarios:
            superior_info = f"→ Superior: {func.superior.nome_completo}" if func.superior else "→ SEM SUPERIOR"
            print(f"      • {func.nome_completo} {superior_info}")
    
    print("\n" + "="*60)
    print("INSTRUÇÕES PARA CONFIGURAR:")
    print("="*60)
    print("""
1. Acesse o Admin Django:
   http://localhost:8000/admin/

2. Vá em 'Core' → 'Setores'

3. Para cada setor, clique em 'Editar'

4. No campo 'Chefe do setor', selecione um funcionário

5. Salve

6. Depois execute:
   python manage.py atualizar_hierarquia

Ou configure via código Python:
   from core.models import Setor
   from funcionarios.models import Funcionario
   
   # Exemplo:
   setor_ti = Setor.objects.get(nome='TI')
   chefe_ti = Funcionario.objects.get(nome_completo='João Silva')
   setor_ti.chefe = chefe_ti
   setor_ti.save()
""")
    
    print("\n" + "="*60)
    
    # Perguntar se quer configurar agora
    print("\n💡 CONFIGURAÇÃO INTERATIVA:")
    print("-" * 60)
    
    resposta = input("\nDeseja configurar os chefes agora? (s/n): ").strip().lower()
    
    if resposta == 's':
        configurar_chefes_interativo()
    else:
        print("\n✅ Use o Admin Django para configurar quando estiver pronto!")

def configurar_chefes_interativo():
    """Configuração interativa dos chefes"""
    setores = Setor.objects.filter(ativo=True, chefe__isnull=True)
    
    for setor in setores:
        print(f"\n🏢 Configurando setor: {setor.nome}")
        print("-" * 60)
        
        funcionarios = setor.funcionarios.filter(status='A')
        
        if not funcionarios.exists():
            print("⚠️  Setor sem funcionários. Pulando...")
            continue
        
        print("\nFuncionários disponíveis:")
        for i, func in enumerate(funcionarios, 1):
            print(f"{i}. {func.nome_completo} - {func.funcao.nome}")
        
        print("0. Pular este setor")
        
        try:
            escolha = int(input("\nEscolha o número do chefe: "))
            
            if escolha == 0:
                continue
            
            if 1 <= escolha <= funcionarios.count():
                chefe = list(funcionarios)[escolha - 1]
                setor.chefe = chefe
                setor.save()
                print(f"✅ {chefe.nome_completo} definido como chefe do setor {setor.nome}")
            else:
                print("❌ Opção inválida!")
        except ValueError:
            print("❌ Entrada inválida!")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("\n" + "="*60)
    print("✅ Configuração concluída!")
    print("\nAgora execute:")
    print("   python manage.py atualizar_hierarquia")
    print("="*60)

if __name__ == '__main__':
    setup_hierarquia()
