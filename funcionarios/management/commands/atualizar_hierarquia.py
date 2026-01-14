"""
Comando para atualizar automaticamente a hierarquia de funcionários
baseada nos chefes de setor
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from funcionarios.models import Funcionario
from core.models import Setor


class Command(BaseCommand):
    help = 'Atualiza a hierarquia de funcionários baseada nos chefes de setor'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a atualização mesmo para funcionários que já têm superior definido',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write('Iniciando atualização da hierarquia...\n')
        
        # Buscar todos os setores com chefe
        setores_com_chefe = Setor.objects.filter(chefe__isnull=False, ativo=True)
        
        total_atualizados = 0
        total_ignorados = 0
        
        for setor in setores_com_chefe:
            self.stdout.write(f'\nProcessando setor: {setor.nome}')
            self.stdout.write(f'  Chefe: {setor.chefe.nome_completo}')
            
            # Buscar funcionários do setor
            if force:
                funcionarios = setor.funcionarios.filter(status='A').exclude(pk=setor.chefe.pk)
            else:
                funcionarios = setor.funcionarios.filter(
                    status='A', 
                    superior__isnull=True
                ).exclude(pk=setor.chefe.pk)
            
            count = funcionarios.count()
            
            if count == 0:
                self.stdout.write(self.style.WARNING(f'  Nenhum funcionário para atualizar'))
                continue
            
            # Atualizar superior
            funcionarios.update(superior=setor.chefe)
            total_atualizados += count
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ {count} funcionário(s) atualizado(s)'))
        
        # Resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'\n✓ Total de funcionários atualizados: {total_atualizados}'))
        
        # Verificar funcionários sem superior
        sem_superior = Funcionario.objects.filter(
            status='A',
            superior__isnull=True
        ).exclude(setor__chefe__isnull=True)
        
        if sem_superior.exists():
            self.stdout.write(self.style.WARNING(f'\n⚠ Funcionários sem superior (setor tem chefe): {sem_superior.count()}'))
            for func in sem_superior:
                self.stdout.write(f'  - {func.nome_completo} ({func.setor.nome})')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('\nAtualização concluída!'))
