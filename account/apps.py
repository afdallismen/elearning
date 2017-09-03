from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _lazy


class AccountConfig(AppConfig):
    name = 'account'
    verbose_name = _lazy("authentication")

    def ready(self):
        import account.signals  # noqa
