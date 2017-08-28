from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'
    verbose_name = 'account'

    def ready(self):
        import account.signals  # noqa
