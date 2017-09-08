import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import ugettext as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from account.utils import user_avatar_directory_path


class MyUser(User):
    class Meta:
        proxy = True
        get_latest_by = "date_joined"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.name

    def __repr__(self):
        return "MyUser(username=\"{username})\"".format(username=self.username)

    @property
    def name(self):
        return (self.get_full_name() or
                self.get_short_name() or
                self.get_username())

    @property
    def is_student(self):
        return hasattr(self, 'student') and self.student is not None

    @property
    def is_lecturer(self):
        return hasattr(self, 'lecturer') and self.lecturer is not None


class BaseAccountModel(models.Model):
    user = models.OneToOneField(
        MyUser,
        editable=False,
        on_delete=models.CASCADE)
    avatar = models.ImageField(
        blank=True,
        default='',
        upload_to=user_avatar_directory_path)
    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 100})

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.name

    def __repr__(self):
        return ("{classname}(user={user})"
                .format(self.__name__, repr(self.user)))


class Student(BaseAccountModel):
    NOBPVALIDATOR = RegexValidator(
        '^[01][0-9]'
        '[01]0{2}'
        '[0-9]{2}$')  # ex: 1510099
    PROGRAM = {
        '0': _("computer system"),
        '1': _("information system")
    }

    nobp = models.CharField(
        max_length=7,
        unique=True,
        validators=[NOBPVALIDATOR],
        verbose_name=_("no. bp"))

    class Meta:
        verbose_name = _("student")
        verbose_name_plural = _("students")

    @property
    def class_of(self):
        if self.nobp:
            return '20{!s}'.format(self.nobp[0:2])
        return str(timezone.now().year)

    @property
    def program(self):
        if self.nobp:
            return (self.PROGRAM[self.nobp[2]]).title()
        return (self.PROGRAM['0']).title()

    @property
    def nobp_sequence(self):
        if self.nobp:
            return self.nobp[5:7]
        return '00'

    @property
    def semester(self):
        now = timezone.now()
        class_of = int(self.class_of)
        is_odd_semester = now.month >= 6
        semester = ((now.year - class_of) * 2)

        if now.year == class_of:
            return 1
        elif is_odd_semester:
            return semester + 1
        else:
            return semester + 2


class Lecturer(BaseAccountModel):
    GENDER = {
        '1': _("male"),
        '2': _("female")
    }
    NIPVALIDATOR = RegexValidator(
        '^[12][09][0-9]{2}[01][0-9][0-9]{2}'
        '[12][09][0-9]{2}[01][0-9]'
        '[12]'
        '[0-9]{3}$')  # ex: 198503302003121002

    nip = models.CharField(
        max_length=18,
        unique=True,
        validators=[NIPVALIDATOR],
        verbose_name=_("no. nip")
    )

    class Meta:
        verbose_name = _("lecturer")
        verbose_name_plural = _("lecturers")

    @property
    def birth_date(self):
        if self.nip:
            return datetime.strptime(self.nip[:8], "%Y%m%d").date()
        return datetime.strptime("19000101", "%Y%m%d").date()

    @property
    def advancement_date(self):
        if self.nip:
            return datetime.strptime(self.nip[8:14], "%Y%m").date()
        return datetime.strptime("190001", "%Y%m").date()

    @property
    def gender(self):
        if self.nip:
            return (self.GENDER[self.nip[14]]).title()
        return (self.GENDER['1']).title()

    @property
    def nip_sequence(self):
        if self.nip:
            return int(self.nip[-3:])
        return "000"
