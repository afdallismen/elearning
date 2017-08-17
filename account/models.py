from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone

from .choices import GENDER_CHOICES
from .utils import user_avatar_directory_path


MALE = GENDER_CHOICES[0][0]  # Default BaseProfile.gender
NOBPVALIDATOR = RegexValidator('^(0[0-9]|1[0-9])(10{2}|00{2})([0-9][0-9])$')  # ex: 1510099  # noqa
PROGRAM = {
    '000': 'Computer System',
    '100': 'Information System'
}


class BaseAccountModel(models.Model):
    user = models.OneToOneField(
        User,
        editable=False,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    avatar = models.ImageField(
        blank=True,
        default='',
        upload_to=user_avatar_directory_path
    )

    class Meta:
        abstract = True

    def __str__(self):
        return (
            self.user.get_full_name() or
            self.user.get_short_name() or
            self.user.get_username()
        )


class Student(BaseAccountModel):
    nobp = models.CharField(
        max_length=7,
        unique=True,
        validators=[NOBPVALIDATOR]
    )

    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'students'

    @property
    def class_of(self):
        if self.nobp:
            return '20{!s}'.format(self.nobp[0:2])
        return str(timezone.now().year)

    @property
    def program(self):
        if self.nobp:
            return PROGRAM[self.nobp[2:5]]
        return PROGRAM['000']

    @property
    def nobp_seq(self):
        if self.nobp:
            return self.nobp[5:7]
        return '00'

    @property
    def in_semester(self):
        year = timezone.now().year
        month = timezone.now().month
        class_of = int(self.class_of)
        is_odd_semester = (12 / 2) <= month
        semester = year - class_of

        if year == class_of:
            return 1
        elif is_odd_semester:
            return (semester * 2) + 1
        else:
            return (semester * 2) + 2


class Lecturer(BaseAccountModel):
    nip = models.CharField(
        max_length=7,
        unique=True,
        validators=[NOBPVALIDATOR]
    )

    class Meta:
        verbose_name = 'lecturer'
        verbose_name_plural = 'lecturers'
