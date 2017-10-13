import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone
from django.utils.translation import ugettext as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from account.utils import user_avatar_directory_path


# Keys depends on other value, read where it's used
GENDER = {'1': _("male"),
          '2': _("female")}
PROGRAM = {'0': _("computer system"),
           '1': _("information system")}


class MyUser(User):
    class Meta:
        get_latest_by = 'date_joined'
        ordering = ['first_name', 'username']
        proxy = True
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.name

    def __repr__(self):
        return "MyUser(username=\"{!s}\")".format(self.username)

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

    @property
    def identity(self):
        if self.is_student:
            return ('student', self.student.nobp)
        elif self.is_lecturer:
            return ('lecturer', self.lecturer.nip)

    @property
    def avatar_thumbnail(self):
        if self.is_student:
            return self.student.avatar_thumbnail
        elif self.is_lecturer:
            return self.lecturer.avatar_thumbnail


class BaseAccountModel(models.Model):
    user = models.OneToOneField(MyUser,
                                editable=False,
                                on_delete=models.CASCADE)
    avatar = models.ImageField(blank=True,
                               default='',
                               upload_to=user_avatar_directory_path)
    avatar_thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(200, 200)],
                                      format='JPEG',
                                      options={'quality': 100})

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.name

    def __repr__(self):
        return ("{!s}(user=\"{!s}\")"
                .format(self.__class__.__name__.title(), self.user))


class Student(BaseAccountModel):
    # NOBPVALIDATOR = RegexValidator('^[01][0-9]'  # Class of: 00 - 19
    #                                '[01]0{2}'  # Program: 000/100
    #                                '[0-9]{2}$')  # Sequence: 00 - 99

    nobp = models.CharField(max_length=9,
                            unique=True,
                            help_text=_("Minimal 9 digit"),
                            validators=[MinLengthValidator(9)],
                            verbose_name=_("no. bp"))

    belong_in = models.ForeignKey('sis.Course',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True,
                                  verbose_name=_("class"))

    class Meta:
        get_latest_by = 'user__date_joined'
        ordering = ['user__first_name', 'user__username']
        verbose_name = _("student")
        verbose_name_plural = _("students")

    def clean(self):
        if self.belong_in and self not in self.belong_in.student_set.all():
            cap = self.belong_in.capacity
            student_count = self.belong_in.student_set.count()
            print([cap, student_count])
            if student_count >= cap:
                raise ValidationError(
                    {'belong_in': _(("This class already full,"
                                     " choose another class"))}
                )

    @property
    def class_of(self):
        if self.nobp:
            return '20{!s}'.format(self.nobp[0:2])
        return str(timezone.now().year)

    # @property
    # def program(self):
    #     if self.nobp:
    #         return (PROGRAM[self.nobp[2]]).title()
    #     return (PROGRAM['0']).title()

    @property
    def nobp_sequence(self):
        if self.nobp:
            return self.nobp[-2]
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
    NIPVALIDATOR = RegexValidator('^[12][09][0-9]{2}[01][0-9][0-9]{2}'  # Birth date: yyyymmdd # noqa
                                  '[12][09][0-9]{2}[01][0-9]'  # Advancedment date: yyyyymmdd  # noqa
                                  '[12]'  # Gender: 1/2
                                  '[0-9]{3}$')  # Sequence: 000 - 999

    nip = models.CharField(max_length=18,
                           unique=True,
                           help_text=_("Minimal 18 digit"),
                           validators=[NIPVALIDATOR],
                           verbose_name=_("no. nip"))

    class Meta:
        get_latest_by = 'user__date_joined'
        ordering = ['user__first_name', 'user__username']
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
            return (GENDER[self.nip[14]]).title()
        return (GENDER['1']).title()

    @property
    def nip_sequence(self):
        if self.nip:
            return int(self.nip[-3:])
        return "000"
