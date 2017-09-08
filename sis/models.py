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


SCORE_VALIDATOR = MaxValueValidator(100)


class Attachment(models.Model):
    FILE_EXTENSION = {
        'image': ['jpg', 'png'],
        'animation': ['swf'],
        'video': ['mp4', 'webm'],
        'doc': ['doc', 'docx', 'xsl', 'xslx', 'ppt', 'pptx', 'pdf']
    }
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
        return "Attachment(file=\"{filename}\")".format(filename=self.filename)

    @property
    def file_name(self):
        return self.file_upload.name.split("/")[-1]

    @property
    def file_extension(self):
        return self.file_upload.name.split(".")[-1].lower()

    @property
    def html_display(self):
        return file_html_display(self, 640, 480)

    @property
    def is_supported(self):
        return self.file_extension in self.SUPPORTED_FILE_EXTENSION

    @property
    def is_viewable(self):
        is_viewable = self.is_image or self.is_animation or self.is_video
        return viewable

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
    created_date = models.DateField(auto_now_add=True,
                                    verbose_name=_("created date"))
    updated_date = models.DateField(auto_now=True,
                                    verbose_name=_("updated date"))
    attachments = GenericRelation(Attachment, verbose_name=_("attachments"))

    class Meta:
        verbose_name = _("module")
        verbose_name_plural = _("modules")

    def __str__(self):
        return self.title

    def __repr__(self):
        return "Question(title=\"{title}\")".format(title=self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Module, self).save(*args, **kwargs)


class Assignment(models.Model):
    CATEGORY_CHOICES = ((0, _("quiz")),
                        (1, _("mid")),
                        (2, _("final")))

    short_description = models.CharField(max_length=100,
                                         verbose_name=_("title"))
    category = models.PositiveIntegerField(choices=CATEGORY_CHOICES,
                                           verbose_name=_("category"))
    created_date = models.DateField(auto_now_add=True,
                                    verbose_name=_("created date"))

    class Meta:
        verbose_name = _("assignment")
        verbose_name_plural = _("assignments")

    def __str__(self):
        if self.short_description:
            return nstrip_tags(30, self.short_description)
        return "{cat} assignment".format(cat=self.get_category_display())

    def __repr__(self):
        if self.short_description:
            return ("Assignment(\"{desc}\")"
                    .format(desc=nstrip_tags(20, self.short_description)))
        return "Assignment{category=\"{cat}\")".format(cat=self.category)


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
        return ("Question(assignment={assignment})"
                .format(assignment=str(self.assignment)))


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
    correct = models.NullBooleanField(blank=True,
                                      verbose_name=_("is it correct ?"))

    class Meta:
        verbose_name = _("answer")
        verbose_name_plural = _("answers")

    def __str__(self):
        if self.text:
            return nstrip_tags(30, self.text)
        return _("This answer has no written text")

    def __repr__(self):
        return ("Answer(question={question}, assignment={assignment})"
                .format(
                    question=str(self.question),
                    str(assignment=self.assignment)))

    def save(self, *args, **kwargs):
        if self.correct is True:
            self.score = 100
        elif self.correct is False:
            self.score = 0
        super(Answer, self).save(*args, **kwargs)


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

    class Meta:
        verbose_name = _("assignment result")
        verbose_name_plural = _("assignment result")

    def __str__(self):
        return self.score

    def __repr__(self):
        return ("AssignmentResult(student={student}, assignment={assignment},"
                "score={score}").format(
                    student=str(self.student),
                    assignment=str(self.assignment),
                    score=self.score)


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
        return ("FinalResult(student={student}, score={score})"
                .format(student=str(self.student), score=self.score))

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
