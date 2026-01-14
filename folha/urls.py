"""
URLs do app Folha de Pagamento
"""
from django.urls import path
from . import views

app_name = 'folha'

urlpatterns = [
    path('', views.folha_list, name='list'),
    path('gerar/', views.folha_gerar, name='gerar'),
    path('<int:pk>/', views.folha_detail, name='detail'),
    path('<int:pk>/fechar/', views.folha_fechar, name='fechar'),
    path('<int:pk>/reabrir/', views.folha_reabrir, name='reabrir'),
    path('<int:pk>/marcar-paga/', views.folha_marcar_paga, name='marcar_paga'),
    path('<int:folha_pk>/item/adicionar/', views.item_adicionar, name='item_adicionar'),
    path('item/<int:pk>/remover/', views.item_remover, name='item_remover'),
    # Eventos
    path('<int:folha_pk>/evento/adiantamento/novo/', views.evento_criar_adiantamento, name='evento_adiantamento_novo'),
    path('<int:folha_pk>/evento/13/novo/', views.evento_criar_decimo_terceiro, name='evento_13_novo'),
    path('evento/<int:pk>/fechar/', views.evento_fechar, name='evento_fechar'),
    path('evento/<int:pk>/reabrir/', views.evento_reabrir, name='evento_reabrir'),
    path('evento/<int:pk>/marcar-pago/', views.evento_marcar_pago, name='evento_marcar_pago'),
    
    # Exportação
    path('<int:pk>/export/pdf/', views.folha_export_pdf, name='export_pdf'),
    path('<int:pk>/export/excel/', views.folha_export_excel, name='export_excel'),
    path('<int:folha_pk>/holerite/<int:funcionario_pk>/', views.holerite_pdf, name='holerite_pdf'),
]
