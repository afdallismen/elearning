from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from tinymce import models as tinymce_models

from account.models import Student
from sis.utils import attachment_directory, nstrip_tags
from sis.validators import MinDateValueValidator


class Attachment(models.Model):
    file_upload = models.FileField(
        upload_to=attachment_directory,
        verbose_name="file upload")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "attachment"
        verbose_name_plural = "attachments"

    def __str__(self):
        return self.file_upload.name


class Module(models.Model):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="title")
    slug = models.SlugField(
        blank=True,
        default="",
        editable=False,
        max_length=100)
    text = tinymce_models.HTMLField(
        blank=True,
        default="",
        verbose_name="text")
    created_date = models.DateField(
        auto_now_add=True,
        verbose_name="created date")
    updated_date = models.DateField(
        auto_now=True,
        verbose_name="updated date")
    attachments = GenericRelation(
        Attachment,
        verbose_name="attachments")

    class Meta:
        verbose_name = "module"
        verbose_name_plural = "modules"

    def __str__(self):
        return "{} - {}".format(self.created_date, self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Module, self).save(*args, **kwargs)


class Assignment(models.Model):
    DUEDATEVALIDATOR = MinDateValueValidator(timezone.now().date())
    ASSIGNMENT_CATEGORY_CHOICES = (
        (0, "Weekly"),
        (1, "Mid semester"),
        (2, "Final"))

    category = models.PositiveIntegerField(
        choices=ASSIGNMENT_CATEGORY_CHOICES,
        verbose_name="category")
    created_date = models.DateField(
        auto_now_add=True,
        verbose_name="created date")

    class Meta:
        verbose_name = "assignment"
        verbose_name_plural = "assignments"

    def __str__(self):
        return "{} - {} assignment".format(
            self.created_date, self.get_category_display())


class Question(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="assignment")
    text = models.TextField(blank=True, default="", verbose_name="text")
    score_percentage = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="score percentage")
    attachments = GenericRelation(Attachment, verbose_name="attachments")

    class Meta:
        verbose_name = "question"
        verbose_name_plural = "questions"

    def __str__(self):
        if self.text:
            return nstrip_tags(30, self.text)
        return "This object has no written text."


class Answer(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="student")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="question")
    text = models.TextField(blank=True, default="", verbose_name="text")
    attachments = GenericRelation(
        Attachment,
        verbose_name="attachments")
    score = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="score")
    correct = models.NullBooleanField(
        blank=True,
        verbose_name="correct")

    class Meta:
        verbose_name = "answer"
        verbose_name_plural = "answers"

    def __str__(self):
        if self.text:
            return nstrip_tags(30, self.text)
        return "This object has no written text."

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
        verbose_name="student")
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        verbose_name="assignment")
    score = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="score")

    class Meta:
        verbose_name = "assignment result"
        verbose_name_plural = "assignment result"

    def __str__(self):
        return "{} result of {}".format(
            self.student,
            self.assignment
        )


class FinalResult(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="student")
    score = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="score")

    class Meta:
        verbose_name = "final result"
        verbose_name_plural = "final result"

    def __str__(self):
        return "Final result of student {}".format(self.student)

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
