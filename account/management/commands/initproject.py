from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from account.models import Lecturer, Student, MyUser
from sis.models import FinalResultPercentage


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

    admin, _ = MyUser.objects.get_or_create(**user['admin'])
    admin.set_password("qweasdzxc")
    admin.save()

    Lecturer.objects.get_or_create(user=admin, nip="198503302003121002")

    afdal, _ = MyUser.objects.get_or_create(**user['student'])
    afdal.set_password("qweasdzxc")
    afdal.save()

    Student.objects.get_or_create(user=afdal, nobp="1510099")


def create_final_result_percentage():
    if not FinalResultPercentage.objects.exists():
        FinalResultPercentage.objects.get_or_create(
            **settings.FINAL_RESULT_PERCENTAGE)


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('refreshdb')
        call_command('creategroups')
        createuser()
        create_final_result_percentage()
