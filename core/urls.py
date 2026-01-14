"""
URLs do app Core
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Lançamentos Fixos Gerais
    path('lancamentos-fixos-gerais/', views.lancamentos_fixos_gerais_list, name='lancamentos_fixos_gerais_list'),
    path('lancamentos-fixos-gerais/novo/', views.lancamentos_fixos_gerais_create, name='lancamentos_fixos_gerais_create'),
    path('lancamentos-fixos-gerais/<int:pk>/editar/', views.lancamentos_fixos_gerais_update, name='lancamentos_fixos_gerais_update'),
    path('lancamentos-fixos-gerais/<int:pk>/excluir/', views.lancamentos_fixos_gerais_delete, name='lancamentos_fixos_gerais_delete'),
]
