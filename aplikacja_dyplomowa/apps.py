from django.apps import AppConfig


class AplikacjaDyplomowaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplikacja_dyplomowa'

    def ready(self):
        import aplikacja_dyplomowa.signals
