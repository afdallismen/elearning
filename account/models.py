from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import ugettext as _


from account.utils import user_avatar_directory_path


NOBPVALIDATOR = RegexValidator(r'^0|1[0-9]0|10{2}[0-9]{2}$')  # ex: 1510099


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

    def name(self):
        return (
            self.user.get_full_name() or
            self.user.get_short_name() or
            self.user.get_username()
        )
    name.short_description = _("name")
    name.admin_order_field = 'user__first_name'

    def __str__(self):
        return self.name()


class Student(BaseAccountModel):
    PROGRAM = {
        '0': _("Computer System"),
        '1': _("Information System")
    }

    nobp = models.CharField(
        max_length=7,
        unique=True,
        validators=[NOBPVALIDATOR],
        verbose_name="no. bp"
    )

    class Meta:
        verbose_name = _('student')
        verbose_name_plural = _('students')

    def class_of(self):
        if self.nobp:
            return '20{!s}'.format(self.nobp[0:2])
        return str(timezone.now().year)
    class_of.short_description = _('class_of')
    class_of.admin_order_field = 'nobp'

    def program(self):
        if self.nobp:
            return self.PROGRAM[self.nobp[2]]
        return self.PROGRAM['0']
    program.short_description = _('program')
    program.admin_order_field = 'nobp'

    def nobp_seq(self):
        if self.nobp:
            return self.nobp[5:7]
        return '00'
    nobp_seq.short_description = _('sequence')
    nobp_seq.admin_order_field = 'nobp'

    def in_semester(self):
        year = timezone.now().year
        month = timezone.now().month
        class_of = int(self.class_of())
        is_odd_semester = (12 / 2) <= month
        semester = year - class_of

        if year == class_of:
            return 1
        elif is_odd_semester:
            return (semester * 2) + 1
        else:
            return (semester * 2) + 2
    in_semester.short_description = _('in_semester')
    in_semester.admin_order_field = 'nobp'


class Lecturer(BaseAccountModel):
    nip = models.CharField(
        max_length=7,
        unique=True,
        validators=[NOBPVALIDATOR],
        verbose_name="no. nip"
    )

    class Meta:
        verbose_name = _('lecturer')
        verbose_name_plural = _('lecturers')
