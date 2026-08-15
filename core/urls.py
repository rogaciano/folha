"""
URLs do app Core
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Setores
    path('setores/', views.setor_list, name='setor_list'),
    path('setores/novo/', views.setor_create, name='setor_create'),
    path('setores/<int:pk>/editar/', views.setor_update, name='setor_update'),
    path('setores/<int:pk>/excluir/', views.setor_delete, name='setor_delete'),
    
    # Funções / Cargos
    path('funcoes/', views.funcao_list, name='funcao_list'),
    path('funcoes/nova/', views.funcao_create, name='funcao_create'),
    path('funcoes/<int:pk>/editar/', views.funcao_update, name='funcao_update'),
    path('funcoes/<int:pk>/excluir/', views.funcao_delete, name='funcao_delete'),
    
    # Tipos de Contrato
    path('tipos-contrato/', views.tipo_contrato_list, name='tipo_contrato_list'),
    path('tipos-contrato/novo/', views.tipo_contrato_create, name='tipo_contrato_create'),
    path('tipos-contrato/<int:pk>/editar/', views.tipo_contrato_update, name='tipo_contrato_update'),
    path('tipos-contrato/<int:pk>/excluir/', views.tipo_contrato_delete, name='tipo_contrato_delete'),
    
    # Proventos e Descontos
    path('proventos-descontos/', views.provento_desconto_list, name='provento_desconto_list'),
    path('proventos-descontos/novo/', views.provento_desconto_create, name='provento_desconto_create'),
    path('proventos-descontos/<int:pk>/editar/', views.provento_desconto_update, name='provento_desconto_update'),
    path('proventos-descontos/<int:pk>/excluir/', views.provento_desconto_delete, name='provento_desconto_delete'),
    
    # Lançamentos Fixos Gerais
    path('lancamentos-fixos-gerais/', views.lancamentos_fixos_gerais_list, name='lancamentos_fixos_gerais_list'),
    path('lancamentos-fixos-gerais/novo/', views.lancamentos_fixos_gerais_create, name='lancamentos_fixos_gerais_create'),
    path('lancamentos-fixos-gerais/<int:pk>/editar/', views.lancamentos_fixos_gerais_update, name='lancamentos_fixos_gerais_update'),
    path('lancamentos-fixos-gerais/<int:pk>/excluir/', views.lancamentos_fixos_gerais_delete, name='lancamentos_fixos_gerais_delete'),
]
