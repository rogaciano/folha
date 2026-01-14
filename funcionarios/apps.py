from django.apps import AppConfig


class FuncionariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'funcionarios'
    verbose_name = 'Funcionários'
    
    def ready(self):
        """Importa os signals quando o app estiver pronto"""
        import funcionarios.signals
