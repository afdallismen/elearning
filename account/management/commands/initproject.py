from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand

from account.models import Lecturer


def createsuperuser():
    user = {
        'username': "admin",
        'first_name': "the",
        'last_name': "admin",
        'email': "admin@email.com",
        'is_active': True,
        'is_staff': True,
        'is_superuser': True
    }

    admin = User.objects.create(**user)
    admin.set_password("qweasdzxc")
    admin.save()

    dosen = Lecturer.objects.get(user=admin)
    dosen.nip = "1510099"
    dosen.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('refreshdb')
        call_command('creategroups')
        createsuperuser()
