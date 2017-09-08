from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create student and lecturer group
        proceed = []
        proceed.append(Group.objects.get_or_create(name="student"))
        proceed.append(Group.objects.get_or_create(name="lecturer"))

        for process in proceed:
            group = process[0]
            created = process[1]
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully created {} group".format(group)
                    )
                )
