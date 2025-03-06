from django.apps import AppConfig


class PhysicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'physics'
    verbose_name = 'Physics Simulations'
    
    def ready(self):
        """Initialize app when Django starts."""
        # Import signals if needed
        pass
