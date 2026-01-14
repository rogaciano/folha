"""
Configuração do Django Admin para o app Core
"""
from django.contrib import admin
from .models import Setor, Funcao, TipoContrato, ProventoDesconto, LancamentoFixoGeral


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'chefe', 'ativo', 'created_at']
    list_filter = ['ativo', 'created_at']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']
    autocomplete_fields = ['chefe']


@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'nivel_salarial_referencia', 'ativo', 'created_at']
    list_filter = ['ativo', 'created_at']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']


@admin.register(TipoContrato)
class TipoContratoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'created_at']
    list_filter = ['ativo', 'created_at']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']


@admin.register(ProventoDesconto)
class ProventoDescontoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo_referencia', 'tipo', 'impacto', 'ativo', 'created_at']
    list_filter = ['tipo', 'impacto', 'ativo', 'created_at']
    search_fields = ['nome', 'codigo_referencia', 'descricao']
    ordering = ['tipo', 'nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'codigo_referencia', 'descricao')
        }),
        ('Configuração', {
            'fields': ('tipo', 'impacto', 'ativo')
        }),
    )


@admin.register(LancamentoFixoGeral)
class LancamentoFixoGeralAdmin(admin.ModelAdmin):
    list_display = ['provento_desconto', 'valor', 'percentual', 'data_inicio', 'data_fim', 'ativo', 'esta_ativo']
    list_filter = ['ativo', 'data_inicio', 'provento_desconto__tipo']
    search_fields = ['provento_desconto__nome', 'observacoes']
    autocomplete_fields = ['provento_desconto']
    ordering = ['-data_inicio']
    
    fieldsets = (
        ('Provento/Desconto', {
            'fields': ('provento_desconto',)
        }),
        ('Valor', {
            'fields': ('valor', 'percentual'),
            'description': 'Preencha apenas um dos campos (valor fixo OU percentual)'
        }),
        ('Período de Vigência', {
            'fields': ('data_inicio', 'data_fim', 'ativo')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
    
    def esta_ativo(self, obj):
        return obj.esta_ativo
    esta_ativo.boolean = True
    esta_ativo.short_description = 'Ativo agora'
