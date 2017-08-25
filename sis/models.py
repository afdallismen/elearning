from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from tinymce import models as tinymce_models

from account.models import Student
from sis.utils import attachment_directory
from sis.validators import MinDateValueValidator


SEMESTER = {
    'odd': _("odd"),
    'even': _("even")
}


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


class Module(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name=_("title"))
    slug = models.SlugField(max_length=100, blank=True, default="")
    content = tinymce_models.HTMLField()
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
        return self.title

    @property
    def semester(self):
        if self.created_date.month <= 6:
            return SEMESTER['even']
        return SEMESTER['odd']

    @property
    def academic_year(self):
        if self.semester == SEMESTER['odd']:
            return "{}/{}".format(
                self.created_date.year - 1,
                self.created_date.year)

        return "{}/{}".format(
            self.created_date.year,
            self.created_date.year + 1)


class Assignment(models.Model):
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

    def __repr__(self):
        return "{} assignment".format(self.get_assignment_type_display())

    def __str__(self):
        return repr(self)

    @property
    def is_active(self):
        return self.due_date >= timezone.now().date()

    @property
    def semester(self):
        if self.created_date.month <= 6:
            return SEMESTER['even']
        return SEMESTER['odd']

    @property
    def academic_year(self):
        if self.semester == SEMESTER['odd']:
            return "{}/{}".format(
                self.created_date.year - 1,
                self.created_date.year)

        return "{}/{}".format(
            self.created_date.year,
            self.created_date.year + 1)


class Question(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        verbose_name=_("assignment"))
    text = models.TextField(blank=True, default="")
    attachments = GenericRelation(
        Attachment,
        verbose_name=_("attachments"))
    score_percentage = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("score percentage"))

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    def __str__(self):
        if self.text:
            return strip_tags(
                self.text[:30] if len(self.text) < 30
                else self.text[:30] + "...")
        return _("No text.")


class Answer(models.Model):
    author = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name=_("author"))
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_("question"))
    text = tinymce_models.HTMLField()
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
            return strip_tags(
                self.text[:30] if len(self.text) < 30
                else self.text[:30] + "...")
        return _("No text.")


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

    def compute_final_score(self):
        questions = self.assignments.question_set.all()
        answers = []
        for question in questions:
            answer = Answer.objects.get(author=self.student, question=question)
            answers.append(answer)
        return sum([answer.score for answer in answers]) // len(questions)
