"""
Configuração do Django Admin para o app Funcionários
"""
from django.contrib import admin
from .models import Funcionario, Contrato, LancamentoFixo, Adiantamento, Ferias


class ContratoInline(admin.TabularInline):
    model = Contrato
    extra = 0
    fields = ['tipo_contrato', 'data_inicio', 'data_fim', 'carga_horaria']


class LancamentoFixoInline(admin.TabularInline):
    model = LancamentoFixo
    extra = 0
    fields = ['provento_desconto', 'valor', 'percentual', 'data_inicio', 'data_fim']


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'funcao', 'setor', 'superior', 'salario_base', 'status', 'participa_folha', 'data_admissao']
    list_filter = ['status', 'participa_folha', 'setor', 'funcao', 'data_admissao']
    search_fields = ['nome_completo', 'cpf', 'email']
    ordering = ['nome_completo']
    date_hierarchy = 'data_admissao'
    autocomplete_fields = ['superior']
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome_completo', 'cpf', 'foto', 'data_nascimento', 'email', 'telefone', 'endereco', 'chave_pix')
        }),
        ('Informações Profissionais', {
            'fields': ('data_admissao', 'funcao', 'setor', 'salario_base', 'superior', 'status', 'participa_folha')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ContratoInline, LancamentoFixoInline]


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['funcionario', 'tipo_contrato', 'data_inicio', 'data_fim', 'carga_horaria', 'esta_ativo']
    list_filter = ['tipo_contrato', 'data_inicio']
    search_fields = ['funcionario__nome_completo', 'funcionario__cpf']
    date_hierarchy = 'data_inicio'
    ordering = ['-data_inicio']
    
    def esta_ativo(self, obj):
        return obj.esta_ativo
    esta_ativo.boolean = True
    esta_ativo.short_description = 'Ativo'


@admin.register(LancamentoFixo)
class LancamentoFixoAdmin(admin.ModelAdmin):
    list_display = ['funcionario', 'provento_desconto', 'valor', 'percentual', 'data_inicio', 'data_fim', 'esta_ativo']
    list_filter = ['provento_desconto__tipo', 'data_inicio']
    search_fields = ['funcionario__nome_completo', 'provento_desconto__nome']
    date_hierarchy = 'data_inicio'
    ordering = ['-data_inicio']
    
    def esta_ativo(self, obj):
        return obj.esta_ativo
    esta_ativo.boolean = True
    esta_ativo.short_description = 'Ativo'


@admin.register(Adiantamento)
class AdiantamentoAdmin(admin.ModelAdmin):
    list_display = ['funcionario', 'data_adiantamento', 'valor', 'status']
    list_filter = ['status', 'data_adiantamento']
    search_fields = ['funcionario__nome_completo', 'funcionario__cpf']
    date_hierarchy = 'data_adiantamento'
    ordering = ['-data_adiantamento']


@admin.register(Ferias)
class FeriasAdmin(admin.ModelAdmin):
    list_display = ['funcionario', 'periodo_aquisitivo_inicio', 'periodo_aquisitivo_fim', 
                    'data_inicio_gozo', 'data_fim_gozo', 'dias_corridos', 'status']
    list_filter = ['status', 'data_inicio_gozo']
    search_fields = ['funcionario__nome_completo', 'funcionario__cpf']
    date_hierarchy = 'data_inicio_gozo'
    ordering = ['-data_inicio_gozo']
    
    fieldsets = (
        ('Funcionário', {
            'fields': ('funcionario',)
        }),
        ('Período Aquisitivo', {
            'fields': ('periodo_aquisitivo_inicio', 'periodo_aquisitivo_fim')
        }),
        ('Gozo das Férias', {
            'fields': ('data_inicio_gozo', 'data_fim_gozo', 'dias_corridos')
        }),
        ('Status', {
            'fields': ('status', 'observacoes')
        }),
    )
