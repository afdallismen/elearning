from django.apps import AppConfig


class SisConfig(AppConfig):
    name = 'sis'
    verbose_name = "student information system"

    def ready(self):
        import sis.signals
