from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from sis.models import FinalResultPercentage


def create_final_result_percentage():
    if not FinalResultPercentage.objects.exists():
        FinalResultPercentage.objects.get_or_create(
            **settings.FINAL_RESULT_PERCENTAGE
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('refreshdb')
        create_final_result_percentage()
