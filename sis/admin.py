import nested_admin

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from django.forms import modelformset_factory

from sis.forms import BaseQuestionFormSet
from sis.list_filters import (
    AcademicYearListFilter as filter_year,
    SemesterListFilter as filter_semester,
    AssignmentTypeListFilter as filter_assignment)
from sis.models import Module, Answer, Attachment, Assignment, Question, Report


class AttachmentInline(nested_admin.NestedGenericStackedInline):
    model = Attachment
    extra = 0


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [AttachmentInline]
    extra = 0
    formset = modelformset_factory(
        Question, fields=("__all__"), formset=BaseQuestionFormSet)


class AssignmentAdmin(nested_admin.NestedModelAdmin):
    list_display = ('assignment_type', 'academic_year', 'semester',
                    'is_active')
    inlines = [QuestionInline]

    def is_active(self, obj):
        return obj.is_active
    is_active.short_description = _("is active")
    is_active.admin_order_field = 'due_date'
    is_active.boolean = True

    def academic_year(self, obj):
        return obj.academic_year
    academic_year.short_description = _("academic year")
    academic_year.admin_order_field = 'created_date'

    def semester(self, obj):
        return (obj.semester).title()
    semester.short_description = _("semester")
    semester.admin_order_field = 'created_date'


class ModuleAdmin(nested_admin.NestedModelAdmin):
    list_display = ('the_title', 'academic_year', 'semester', 'updated_date')
    search_fields = ('title', )
    inlines = [AttachmentInline]
    prepopulated_fields = {"slug": ("title",)}

    def the_title(self, obj):
        return (obj.title).title()
    the_title.short_description = _("title")
    the_title.admin_order_field = 'title'

    def academic_year(self, obj):
        return obj.academic_year
    academic_year.short_description = _("academic year")
    academic_year.admin_order_field = 'created_date'

    def semester(self, obj):
        return (obj.semester).title()
    semester.short_description = _("semester")
    semester.admin_order_field = 'created_date'


class AnswerAdmin(nested_admin.NestedModelAdmin):
    search_fields = ('author__user__username', )
    list_filter = (filter_year, filter_semester, filter_assignment)
    list_display = ('answer', 'author_link', 'question_link')
    inlines = [AttachmentInline]

    def answer(self, obj):
        return str(obj)
    answer.short_description = _("answer")
    answer.admin_order_field = 'pk'

    def author_link(self, obj):
        return format_html(
            "<a href={}>{}</a>",
            "".join((
                reverse("admin:account_student_changelist", ),
                "?q={}".format(str(obj.author).replace(" ", "+")))),
            str(obj.author).title()
        )
    author_link.short_description = _("author")
    author_link.admin_order_field = 'author'

    def question_link(self, obj):
        return format_html(
            "<a href={}>{}</a>",
            reverse(
                "admin:sis_assignment_change",
                args=(obj.question.assignment.pk, )),
            str(obj.question))
    question_link.short_description = _("question")
    question_link.admin_order_field = 'question'


admin.site.register(Module, ModuleAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Report)
