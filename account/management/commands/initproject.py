from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand

from account.models import Lecturer, Student


def createuser():
    user = {
        'admin': {
            'username': "admin",
            'first_name': "the",
            'last_name': "admin",
            'email': "admin@email.com",
            'is_active': True,
            'is_staff': True,
            'is_superuser': True},
        'student': {
            'username': "afdallismen",
            'first_name': "afdal",
            'last_name': "lismen",
            'email': "afdal.lismen@gmail.com"},
    }

    admin = User.objects.create(**user['admin'])
    admin.set_password("qweasdzxc")
    admin.save()

    dosen = Lecturer.objects.get(user=admin)
    dosen.nip = "1510099"
    dosen.save()

    afdal = User.objects.create(**user['student'])
    afdal.set_password("qweasdzxc")
    afdal.save()

    student = Student.objects.get(user=afdal)
    student.nobp = "1510099"
    student.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('refreshdb')
        call_command('creategroups')
        createuser()
