from django.db import models
from django.contrib.auth.models import User

from .choices import GENDER_CHOICES, PROGRAM_CHOICES
from .utils import user_directory_path


MALE = GENDER_CHOICES[0][0]  # Default BaseProfile.gender
INFORMATION_SYSTEM = PROGRAM_CHOICES[0][0]  # Default Student.program


class BaseProfile(models.Model):

    GENDER_CHOICES = GENDER_CHOICES

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(
        choices=GENDER_CHOICES,
        default=MALE,
        max_length=1
    )
    birth_date = models.DateField()
    age = models.PositiveSmallIntegerField(
        default=0,
        editable=False,
    )
    avatar = models.ImageField(
        blank=True,
        default='',
        upload_to=user_directory_path
    )

    class Meta:
        abstract = True


class Lecturer(BaseProfile):
    pass


class Student(BaseProfile):

    PROGRAM_CHOICES = PROGRAM_CHOICES

    class_of = models.PositiveSmallIntegerField(default=1900)
    program = models.CharField(
        choices=PROGRAM_CHOICES,
        default=INFORMATION_SYSTEM,
        max_length=2
    )
