"""
URL configuration for folha_pagamento project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # URLs de autenticação
    path('', include('core.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    path('folha/', include('folha.urls')),
]

# Configuração do Admin
admin.site.site_header = "Sistema de Folha de Pagamento"
admin.site.site_title = "Folha de Pagamento"
admin.site.index_title = "Administração"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Browser Reload (Development only)
    urlpatterns = [
        path("__reload__/", include("django_browser_reload.urls")),
    ] + urlpatterns
