"""
Management command para criar contratos para funcionários sem contrato
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from funcionarios.models import Funcionario, Contrato
from core.models import TipoContrato


class Command(BaseCommand):
    help = 'Cria contratos CLT para funcionários que não possuem contrato'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write("CRIANDO CONTRATOS PARA OS FUNCIONÁRIOS")
        self.stdout.write("="*80 + "\n")

        # Busca ou cria o tipo de contrato CLT
        tipo_contrato, created = TipoContrato.objects.get_or_create(
            nome='CLT',
            defaults={
                'descricao': 'Contrato CLT - Regime de Trabalho',
                'ativo': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Tipo de contrato 'CLT' criado"))
        else:
            self.stdout.write(f"✓ Usando tipo de contrato existente: {tipo_contrato.nome}")

        # Busca funcionários sem contrato
        funcionarios = Funcionario.objects.all()
        contratos_criados = 0

        self.stdout.write(f"\nProcessando {funcionarios.count()} funcionários...\n")

        with transaction.atomic():
            for funcionario in funcionarios:
                # Verifica se já tem contrato
                if funcionario.contratos.exists():
                    self.stdout.write(
                        self.style.WARNING(f"  ⊘ {funcionario.nome_completo} - Já possui contrato")
                    )
                    continue
                
                # Cria contrato a partir da data de admissão
                contrato = Contrato.objects.create(
                    funcionario=funcionario,
                    tipo_contrato=tipo_contrato,
                    data_inicio=funcionario.data_admissao,
                    data_fim=None,  # Sem data fim = ativo indefinidamente
                    carga_horaria=44  # 44 horas semanais (padrão CLT)
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {funcionario.nome_completo} - Contrato criado (início: {contrato.data_inicio})"
                    )
                )
                contratos_criados += 1

        self.stdout.write("\n" + "="*80)
        self.stdout.write(f"RESUMO: {contratos_criados} contrato(s) criado(s)")
        self.stdout.write("="*80 + "\n")

        if contratos_criados > 0:
            self.stdout.write(
                self.style.SUCCESS("\n✓ Contratos criados com sucesso!")
            )
            self.stdout.write("  Agora você pode gerar a folha de pagamento novamente.")
            self.stdout.write("  Os funcionários aparecerão na folha.\n")
        else:
            self.stdout.write(
                self.style.WARNING("\n⚠️ Todos os funcionários já possuem contratos.\n")
            )
