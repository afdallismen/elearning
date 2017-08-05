from django.utils import timezone


THIS_YEAR = timezone.now().year
YEARS_RANGE = range(THIS_YEAR-9, THIS_YEAR + 1)

CLASS_OF_YEAR
GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

PROGRAM_CHOICES = (
    ('IS', 'Information System'),
    ('CS', 'Computer System'),
)
