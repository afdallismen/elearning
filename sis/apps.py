from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SisConfig(AppConfig):
    name = 'sis'
    verbose_name = _("student information system")
