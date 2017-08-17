from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.create_group_if_not_exist(name="student")
        self.create_group_if_not_exist(name="lecturer")

    def create_group_if_not_exist(self, name):
        _, created = Group.objects.get_or_create(name=name)
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created {} group'.format(name)
                )
            )
