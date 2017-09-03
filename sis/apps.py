from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _lazy


class SisConfig(AppConfig):
    name = 'sis'
    verbose_name = _lazy("student learning system")

    def ready(self):
        import sis.signals  # noqa
