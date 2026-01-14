"""
Configuração do Django Admin para o app Folha de Pagamento
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import FolhaPagamento, EventoPagamento, ItemFolha, ResumoFolhaFuncionario


class EventoPagamentoInline(admin.TabularInline):
    """Inline para eventos de pagamento na folha"""
    model = EventoPagamento
    extra = 0
    fields = ['tipo_evento', 'descricao', 'data_evento', 'status', 'valor_total']
    readonly_fields = ['valor_total']
    show_change_link = True


class ItemFolhaInline(admin.TabularInline):
    """Inline para itens da folha no evento de pagamento"""
    model = ItemFolha
    extra = 0
    fields = ['funcionario', 'provento_desconto', 'valor_lancado', 'base_calculo']
    readonly_fields = ['funcionario', 'provento_desconto']


@admin.register(FolhaPagamento)
class FolhaPagamentoAdmin(admin.ModelAdmin):
    list_display = ['periodo_referencia', 'status_badge', 'data_fechamento', 
                    'total_proventos', 'total_descontos', 'total_liquido']
    list_filter = ['status', 'ano', 'mes']
    search_fields = ['mes', 'ano']
    ordering = ['-ano', '-mes']
    
    fieldsets = (
        ('Período', {
            'fields': ('mes', 'ano')
        }),
        ('Status', {
            'fields': ('status', 'data_fechamento')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EventoPagamentoInline]
    
    def status_badge(self, obj):
        colors = {
            'R': '#6c757d',  # Cinza
            'F': '#0d6efd',  # Azul
            'P': '#198754',  # Verde
            'C': '#dc3545',  # Vermelho
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def total_proventos(self, obj):
        return f"R$ {obj.total_proventos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    total_proventos.short_description = 'Total Proventos'
    
    def total_descontos(self, obj):
        return f"R$ {obj.total_descontos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    total_descontos.short_description = 'Total Descontos'
    
    def total_liquido(self, obj):
        return f"R$ {obj.total_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    total_liquido.short_description = 'Total Líquido'


@admin.register(EventoPagamento)
class EventoPagamentoAdmin(admin.ModelAdmin):
    """Admin para eventos de pagamento"""
    list_display = ['folha_pagamento', 'tipo_evento', 'descricao', 'data_evento', 
                    'status_badge', 'valor_total_formatado']
    list_filter = ['status', 'tipo_evento', 'folha_pagamento__ano', 'folha_pagamento__mes']
    search_fields = ['descricao', 'folha_pagamento__mes', 'folha_pagamento__ano']
    ordering = ['folha_pagamento', 'data_evento']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('folha_pagamento', 'tipo_evento', 'descricao')
        }),
        ('Datas', {
            'fields': ('data_evento', 'data_pagamento')
        }),
        ('Status e Valores', {
            'fields': ('status', 'valor_total')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['valor_total']
    inlines = [ItemFolhaInline]
    
    def status_badge(self, obj):
        colors = {
            'R': '#6c757d',  # Cinza
            'F': '#0d6efd',  # Azul
            'P': '#198754',  # Verde
            'C': '#dc3545',  # Vermelho
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def valor_total_formatado(self, obj):
        return f"R$ {obj.valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    valor_total_formatado.short_description = 'Valor Total'


@admin.register(ItemFolha)
class ItemFolhaAdmin(admin.ModelAdmin):
    list_display = ['evento_pagamento', 'funcionario', 'provento_desconto', 'tipo_item', 
                    'valor_lancado', 'adiantamento_link']
    list_filter = ['evento_pagamento__folha_pagamento__ano', 'evento_pagamento__folha_pagamento__mes', 
                   'provento_desconto__tipo', 'evento_pagamento__tipo_evento']
    search_fields = ['funcionario__nome_completo', 'provento_desconto__nome']
    ordering = ['evento_pagamento', 'funcionario']
    raw_id_fields = ['adiantamento_origem']
    
    def tipo_item(self, obj):
        colors = {
            'Provento': '#198754',
            'Desconto': '#dc3545',
        }
        tipo = obj.tipo_item
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(tipo, '#000'),
            tipo
        )
    tipo_item.short_description = 'Tipo'
    
    def adiantamento_link(self, obj):
        """Exibe link para o adiantamento origem (rastreabilidade)"""
        if obj.adiantamento_origem:
            from django.urls import reverse
            url = reverse('admin:funcionarios_adiantamento_change', args=[obj.adiantamento_origem.pk])
            return format_html(
                '<a href="{}" title="Ver adiantamento original">'
                '<span style="color: #0d6efd;">📋 {}</span></a>',
                url,
                obj.adiantamento_origem.data_adiantamento.strftime('%d/%m/%Y')
            )
        return '-'
    adiantamento_link.short_description = 'Adiant. Origem'


@admin.register(ResumoFolhaFuncionario)
class ResumoFolhaFuncionarioAdmin(admin.ModelAdmin):
    list_display = ['folha_pagamento', 'funcionario', 'total_proventos', 'total_descontos', 'valor_liquido']
    list_filter = ['folha_pagamento__ano', 'folha_pagamento__mes']
    search_fields = ['funcionario__nome_completo']
    ordering = ['folha_pagamento', 'funcionario']
