from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from tinymce import models as tinymce_models

from account.models import Student
from sis.utils import attachment_directory, nstrip_tags
from sis.validators import MinDateValueValidator


SEMESTER = {
    'odd': _("odd"),
    'even': _("even")
}


class TimedModelMixin(object):

    @property
    def semester(self):
        if self.created_date.month <= 6:
            return SEMESTER['even']
        return SEMESTER['odd']

    @property
    def academic_year(self):
        if self.semester == SEMESTER['even']:
            return "{}/{}".format(
                self.created_date.year - 1,
                self.created_date.year)

        return "{}/{}".format(
            self.created_date.year,
            self.created_date.year + 1)


class Attachment(models.Model):
    file_upload = models.FileField(
        upload_to=attachment_directory,
        verbose_name=_("file upload"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

    def __str__(self):
        return self.file_upload.name


class Module(models.Model, TimedModelMixin):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("title"))
    slug = models.SlugField(
        blank=True,
        default="",
        editable=False,
        max_length=100)
    text = tinymce_models.HTMLField(
        blank=True,
        default="",
        verbose_name=_("text"))
    created_date = models.DateField(
        auto_now_add=True,
        verbose_name=_("created date"))
    updated_date = models.DateField(
        auto_now=True,
        verbose_name=_("updated date"))
    attachments = GenericRelation(
        Attachment,
        verbose_name=_("attachments"))

    class Meta:
        verbose_name = _("module")
        verbose_name_plural = _("modules")

    def __str__(self):
        return "{} - {}".format(self.academic_year, self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Module, self).save(*args, **kwargs)


class Assignment(models.Model, TimedModelMixin):
    DUEDATEVALIDATOR = MinDateValueValidator(timezone.now().date())
    ASSIGNMENT_TYPE_CHOICES = (
        (0, _("Daily")),
        (1, _("Mid semester")),
        (2, _("Final")))

    assignment_type = models.PositiveIntegerField(
        choices=ASSIGNMENT_TYPE_CHOICES,
        verbose_name=_("assignment type"))
    due_date = models.DateField(
        validators=[DUEDATEVALIDATOR],
        verbose_name=_("due date"))
    created_date = models.DateField(
        auto_now_add=True,
        verbose_name=_("created date"))

    class Meta:
        verbose_name = _("assignment")
        verbose_name_plural = _("assignments")

    def __str__(self):
        return "{} - {} assignment".format(
            self.academic_year,
            self.get_assignment_type_display())

    @property
    def is_active(self):
        return self.due_date >= timezone.now().date()


class Question(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("assignment"))
    text = models.TextField(blank=True, default="", verbose_name=_("text"))
    score_percentage = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("score percentage"))
    attachments = GenericRelation(Attachment, verbose_name=_("attachments"))

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    def __str__(self):
        if self.text:
            return nstrip_tags(30, self.text)
        return _("This object has no written text.")


class Answer(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name=_("student"))
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_("question"))
    text = models.TextField(blank=True, default="", verbose_name=_("text"))
    attachments = GenericRelation(
        Attachment,
        verbose_name=_("attachments"))
    score = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("score"))

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("answers")

    def __str__(self):
        if self.text:
            return nstrip_tags(30, self.text)
        return _("This object has no written text.")


class Report(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name=_("student"))
    assignments = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        verbose_name=_("assignment"))
    final_score = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("final score"))

    class Meta:
        verbose_name = _("report")
        verbose_name_plural = _("report")
