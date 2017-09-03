from django.conf import settings
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
from sis.utils import attachment_directory, nstrip_tags, file_html_display
from sis.validators import MinDateValueValidator


class Attachment(models.Model):
    file_upload = models.FileField(
        upload_to=attachment_directory,
        verbose_name=_("file upload"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "attachment"
        verbose_name_plural = "attachments"

    def __str__(self):
        return self.file_upload.name.split("/")[-1]

    @property
    def html_display(self):
        return file_html_display(self.file_upload, 640, 480)


class Module(models.Model):
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
    attachments = GenericRelation(Attachment, verbose_name=_("attachments"))

    class Meta:
        verbose_name = _("module")
        verbose_name_plural = _("modules")

    def __str__(self):
        return "{} / {}".format(self.created_date, self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Module, self).save(*args, **kwargs)


class Assignment(models.Model):
    DUEDATEVALIDATOR = MinDateValueValidator(timezone.now().date())
    ASSIGNMENT_CATEGORY_CHOICES = (
        (0, _("quiz")),
        (1, _("mid")),
        (2, _("final")))

    category = models.PositiveIntegerField(
        choices=ASSIGNMENT_CATEGORY_CHOICES,
        verbose_name=_("category"))
    created_date = models.DateField(
        auto_now_add=True,
        verbose_name=_("created date"))

    class Meta:
        verbose_name = _("assignment")
        verbose_name_plural = _("assignments")

    def __str__(self):
        return "{} / {} assignment".format(
            self.created_date, self.get_category_display())


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
            return "{} / Question {}".format(
                self.assignment, nstrip_tags(30, self.text))
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
    attachments = GenericRelation(Attachment, verbose_name=_("attachments"))
    score = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("score"))
    correct = models.NullBooleanField(
        blank=True,
        verbose_name=_("is it correct ?"))

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("answers")

    def __str__(self):
        if self.text:
            return nstrip_tags(30, self.text)
        return _("This object has no written text.")

    def save(self, *args, **kwargs):
        if self.correct is True:
            self.score = 100
        elif self.correct is False:
            self.score = 0
        super(Answer, self).save(*args, **kwargs)


class AssignmentResult(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name=_("student"))
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        verbose_name=_("assignment"))
    score = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("score"))

    class Meta:
        verbose_name = _("assignment result")
        verbose_name_plural = _("assignment result")

    def __str__(self):
        return _("{} result of {}".format(
            self.student,
            self.assignment))


class FinalResult(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        verbose_name=_("student"))
    score = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("score"))

    class Meta:
        verbose_name = _("final result")
        verbose_name_plural = _("final result")

    def __str__(self):
        return _("Final result of {}".format(self.student))

    @property
    def letter_value(self):
        if 85 <= self.score <= 100:
            return 'A'
        elif 75 <= self.score <= 84:
            return 'B'
        elif 60 <= self.score <= 74:
            return 'C'
        elif 50 <= self.score <= 59:
            return 'D'
        else:
            return 'E'


class FinalResultPercentage(models.Model):
    quiz = models.PositiveSmallIntegerField(
        blank=True,
        default=settings.FINAL_RESULT_PERCENTAGE['quiz'],
        verbose_name=_("quiz"))
    mid = models.PositiveSmallIntegerField(
        blank=True,
        default=settings.FINAL_RESULT_PERCENTAGE['mid'],
        verbose_name=_("mid"))
    final = models.PositiveSmallIntegerField(
        blank=True,
        default=settings.FINAL_RESULT_PERCENTAGE['final'],
        verbose_name=_("final"))

    class Meta:
        verbose_name = _("final result percentage")
        verbose_name_plural = _("final result percentage")
