from urllib.parse import urlencode

from django.conf import settings
from django.contrib.admin.models import LogEntry,  CHANGE
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from tinymce import models as tinymce_models

from account.models import Student
from sis.utils import (
    attachment_directory, nstrip_tags, file_html_display, FILE_EXTENSION)


SCORE_VALIDATOR = MaxValueValidator(100)


class Course(models.Model):
    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name=_("class name"))
    capacity = models.PositiveSmallIntegerField(
        default=1,
        help_text=_("Class max capacity"),
        verbose_name=_("capacity")
    )

    class Meta:
        verbose_name = _("class")
        verbose_name_plural = _("class")

    def __repr__(self):
        return "Course(name=\"{!s}\")".format(self.name)

    def __str__(self):
        return self.name


class Attachment(models.Model):
    SUPPORTED_FILE_EXTENSION = [*FILE_EXTENSION['image'],
                                *FILE_EXTENSION['animation'],
                                *FILE_EXTENSION['video'],
                                *FILE_EXTENSION['doc']]
    file_upload = models.FileField(upload_to=attachment_directory,
                                   verbose_name=_("file upload"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "attachment"
        verbose_name_plural = "attachments"

    def __str__(self):
        return self.file_name

    def __repr__(self):
        return "Attachment(file=\"{!s}\")".format(self.file_name)

    @property
    def file_name(self):
        return self.file_upload.name.split("/")[-1].split(".")[0]

    @property
    def file_extension(self):
        return self.file_upload.name.split(".")[-1].lower()

    @property
    def ext_link(self):
        encoded = urlencode(
            {'': "http://localhost:8000" + self.file_upload.url}
        )[1:]
        return ("http://view.officeapps.live.com/op/view.aspx",
                "?src={!s}").format(encoded)

    @property
    def html_display(self):
        return file_html_display(self, 640, 480)

    @property
    def is_supported(self):
        return self.file_extension in self.SUPPORTED_FILE_EXTENSION

    @property
    def is_viewable(self):
        is_viewable = self.is_image or self.is_animation or self.is_video
        return is_viewable

    @property
    def is_image(self):
        is_image = self.file_extension in self.FILE_EXTENSION['image']
        return self.is_supported and is_image

    @property
    def is_animation(self):
        is_animation = self.file_extension in self.FILE_EXTENSION['animation']
        return self.is_supported and is_animation

    @property
    def is_video(self):
        is_video = self.file_extension in self.FILE_EXTENSION['video']
        return self.is_supported and is_video

    @property
    def is_doc(self):
        is_doc = self.file_extension in self.FILE_EXTENSION['doc']
        return self.is_supported and is_doc


class Module(models.Model):
    title = models.CharField(max_length=100,
                             unique=True,
                             verbose_name=_("title"))
    slug = models.SlugField(blank=True,
                            default="",
                            editable=False,
                            max_length=100)
    text = tinymce_models.HTMLField(blank=True,
                                    default="",
                                    verbose_name=_("text"))
    created_on = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_("created on"))
    attachments = GenericRelation(Attachment, verbose_name=_("attachments"))

    class Meta:
        get_latest_by = 'created_on'
        verbose_name = _("module")
        verbose_name_plural = _("modules")

    def __str__(self):
        return self.title

    def __repr__(self):
        return "Question(title=\"{!s}\")".format(self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Module, self).save(*args, **kwargs)


class Assignment(models.Model):
    CATEGORY_CHOICES = ((0, _("exercise")),
                        (1, _("quiz")),
                        (2, _("mid")),
                        (3, _("final")))

    short_description = models.CharField(max_length=100,
                                         blank=True,
                                         default="",
                                         verbose_name=_("short description"))
    category = models.PositiveIntegerField(choices=CATEGORY_CHOICES,
                                           verbose_name=_("category"))
    created_on = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_("created on"))
    for_class = models.ManyToManyField(
        Course,
        help_text=_("Choose classes who can see this assignment"),
        verbose_name=_("class")
    )
    due = models.DateTimeField(
        validators=[MinValueValidator(timezone.now())],
        help_text=_("Time limit on when student can still submit his/her",
                    " answer for this assignment"),
        verbose_name=_("due time")
    )

    class Meta:
        verbose_name = _("assignment")
        verbose_name_plural = _("assignments")

    def __str__(self):
        if self.short_description:
            return nstrip_tags(30, self.short_description)
        return "{!s} assignment".format(self.get_category_display())

    def __repr__(self):
        if self.short_description:
            return ("Assignment(short_description=\"{!s}\")"
                    .format(nstrip_tags(20, self.short_description)))
        return "Assignment(category=\"{!s}\")".format(self.category)

    @property
    def has_expired(self):
        return timezone.now() > self.due


class Question(models.Model):
    assignment = models.ForeignKey(Assignment,
                                   blank=True,
                                   null=True,
                                   on_delete=models.CASCADE,
                                   verbose_name=_("assignment"))
    text = models.TextField(blank=True, default="", verbose_name=_("text"))
    score_percentage = models.PositiveIntegerField(
        blank=True,
        default=0,
        validators=[SCORE_VALIDATOR],
        verbose_name=_("score percentage"))
    attachments = GenericRelation(Attachment, verbose_name=_("attachments"))

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    def __str__(self):
        if self.text:
            return nstrip_tags(30, self.text)
        return _("This question has no written text")

    def __repr__(self):
        return ("Question(assignment={!s})".format(self.assignment))


class Answer(models.Model):
    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE,
                                verbose_name=_("student"))
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE,
                                 verbose_name=_("question"))
    text = models.TextField(blank=True, default="", verbose_name=_("text"))
    attachments = GenericRelation(Attachment, verbose_name=_("attachments"))
    score = models.PositiveIntegerField(blank=True,
                                        default=0,
                                        validators=[SCORE_VALIDATOR],
                                        verbose_name=_("score"))
    correct = models.NullBooleanField(
        blank=True,
        help_text=_("yes, mean its 100% true, false otherwise"),
        verbose_name=_("is it correct ?")
    )

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("answers")

    def __init__(self, *args, **kwargs):
        super(Answer, self).__init__(*args, **kwargs)
        self.examined = False

    def __str__(self):
        if self.text:
            return nstrip_tags(30, self.text)
        return _("This answer has no written text")

    def __repr__(self):
        return ("Answer(question={!s}, assignment={!s})"
                .format(self.question, self.question.assignment))

    def clean(self):
        assignment = self.question.assignment
        if assignment.has_expired:
            raise ValidationError(_("You can't make an answer"
                                  " for an assignment that already expired"))

    def save(self, *args, **kwargs):
        if self.correct is True:
            self.score = 100
        elif self.correct is False:
            self.score = 0
        super(Answer, self).save(*args, **kwargs)

    @property
    def has_examined(self):
        if not self.examined:
            ct = ContentType.objects.get_for_model(self)
            self.examined = LogEntry.objects.filter(
                user__is_staff=True,
                content_type=ct,
                object_id=self.id,
                action_flag=CHANGE).exists()
        return self.examined


class AssignmentResultManager(models.Manager):
    def get_score(self, student, assignment):
        try:
            score = self.get(student=student, assignment=assignment).score
        except AssignmentResult.DoesNotExist:
            score = 0
        return score


class AssignmentResult(models.Model):
    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE,
                                verbose_name=_("student"))
    assignment = models.ForeignKey(Assignment,
                                   on_delete=models.CASCADE,
                                   verbose_name=_("assignment"))
    score = models.PositiveIntegerField(blank=True,
                                        default=0,
                                        validators=[SCORE_VALIDATOR],
                                        verbose_name=_("score"))
    objects = AssignmentResultManager()

    class Meta:
        verbose_name = _("assignment result")
        verbose_name_plural = _("assignment result")

    def __str__(self):
        return self.score

    def __repr__(self):
        return ("AssignmentResult(student={!s}, assignment={!s},"
                "score={!s}").format(
                    self.student,
                    self.assignment,
                    self.score)


class FinalResult(models.Model):
    student = models.OneToOneField(Student,
                                   on_delete=models.CASCADE,
                                   verbose_name=_("student"))
    score = models.PositiveIntegerField(blank=True,
                                        default=0,
                                        validators=[SCORE_VALIDATOR],
                                        verbose_name=_("score"))

    class Meta:
        verbose_name = _("final result")
        verbose_name_plural = _("final result")

    def __str__(self):
        return self.score

    def __repr__(self):
        return ("FinalResult(student={!s}, score={!s})"
                .format(self.student, self.score))


class FinalResultPercentage(models.Model):
    exercise = models.PositiveSmallIntegerField(
        blank=True,
        default=settings.FINAL_RESULT_PERCENTAGE['exercise'],
        verbose_name=_("exercise")
    )
    quiz = models.PositiveSmallIntegerField(
        blank=True,
        default=settings.FINAL_RESULT_PERCENTAGE['quiz'],
        verbose_name=_("quiz")
    )
    mid = models.PositiveSmallIntegerField(
        blank=True,
        default=settings.FINAL_RESULT_PERCENTAGE['mid'],
        verbose_name=_("mid")
    )
    final = models.PositiveSmallIntegerField(
        blank=True,
        default=settings.FINAL_RESULT_PERCENTAGE['final'],
        verbose_name=_("final")
    )

    class Meta:
        verbose_name = _("final result percentage")
        verbose_name_plural = _("final result percentage")
