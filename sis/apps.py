from django.apps import AppConfig


class SisConfig(AppConfig):
    name = 'sis'
    verbose_name = "courses information system"

    def ready(self):
        import sis.signals
