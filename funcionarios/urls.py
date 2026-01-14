"""
URLs do app Funcionários
"""
from django.urls import path
from . import views

app_name = 'funcionarios'

urlpatterns = [
    # Funcionários
    path('', views.funcionario_list, name='list'),
    path('organograma/', views.organograma, name='organograma'),
    path('<int:pk>/', views.funcionario_detail, name='detail'),
    path('novo/', views.funcionario_create, name='create'),
    path('<int:pk>/editar/', views.funcionario_update, name='update'),
    
    # Contratos
    path('<int:funcionario_pk>/contratos/novo/', views.contrato_create, name='contrato_create'),
    path('contratos/<int:pk>/editar/', views.contrato_update, name='contrato_update'),
    path('contratos/<int:pk>/excluir/', views.contrato_delete, name='contrato_delete'),
    
    # Adiantamentos
    path('adiantamentos/', views.adiantamento_list, name='adiantamento_list'),
    path('adiantamentos/massivo/', views.adiantamento_massivo, name='adiantamento_massivo'),
    
    # Lançamentos Fixos
    path('<int:funcionario_pk>/lancamentos/novo/', views.lancamento_fixo_create, name='lancamento_fixo_create'),
    path('lancamentos/<int:pk>/editar/', views.lancamento_fixo_update, name='lancamento_fixo_update'),
    path('lancamentos/<int:pk>/excluir/', views.lancamento_fixo_delete, name='lancamento_fixo_delete'),
    
    # Férias
    path('ferias/', views.ferias_list, name='ferias_list'),
    path('<int:funcionario_pk>/ferias/novo/', views.ferias_create, name='ferias_create'),
    path('ferias/<int:pk>/editar/', views.ferias_update, name='ferias_update'),
    path('ferias/<int:pk>/excluir/', views.ferias_delete, name='ferias_delete'),
]
