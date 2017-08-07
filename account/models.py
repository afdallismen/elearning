from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from .choices import GENDER_CHOICES
from .utils import user_directory_path


MALE = GENDER_CHOICES[0][0]  # Default BaseProfile.gender
NOBPVALIDATOR = RegexValidator('^(0[1-9]|1[1-9])(10{2}|00{2})([0-9][0-9])$')


class Student(models.Model):

    GENDER_CHOICES = GENDER_CHOICES

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nobp = models.CharField(
        max_length=7,
        validators=[NOBPVALIDATOR]
    )
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
