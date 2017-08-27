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
    AssignmentTypeListFilter as filter_assignment,
    AssignmentActiveListFilter as filter_active)
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
                    'is_active', 'object_action')
    list_display_links = None
    list_filter = (filter_year, filter_semester, filter_active)
    inlines = [QuestionInline]

    class Media:
        css = {
            'all': (
                "font-awesome-4.7.0/css/font-awesome.min.css",
            )
        }

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

    def object_action(self, obj):
        return format_html(
            '<a href="{}" style="margin-right:10px">'
            '<i class="fa fa-file-text-o" aria-hidden="true"></i> Tugas'
            '</a>',
            reverse("admin:sis_assignment_change", args=(obj.id, )),
        )
    object_action.short_description = _("object action")


class ModuleAdmin(nested_admin.NestedModelAdmin):
    list_display = ('the_title', 'academic_year', 'semester', 'updated_date',
                    'object_action')
    list_display_links = None
    list_filter = (filter_year, filter_semester)
    search_fields = ('title', )
    inlines = [AttachmentInline]

    class Media:
        css = {
            'all': (
                "font-awesome-4.7.0/css/font-awesome.min.css",
            )
        }

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

    def object_action(self, obj):
        return format_html(
            '<a href="{}" style="margin-right:10px">'
            '<i class="fa fa-file-text-o" aria-hidden="true"></i> Bahan kuliah'
            '</a>',
            reverse("admin:sis_module_change", args=(obj.id, )),
        )
    object_action.short_description = _("object action")


class AnswerAdmin(nested_admin.NestedModelAdmin):
    search_fields = (
        'author__user__username',
        'author__user__first_name',
        'author__user__last_name')
    list_filter = (filter_year, filter_semester, filter_assignment,
                   ('student', admin.RelatedOnlyFieldListFilter))
    list_display = ('student', 'assignment', 'question', 'score',
                    'object_action')
    list_display_links = None
    inlines = [AttachmentInline]

    class Media:
        css = {
            'all': (
                "font-awesome-4.7.0/css/font-awesome.min.css",
            )
        }

    def assignment(self, obj):
        return obj.question.assignment

    def object_action(self, obj):
        return format_html(
            '<a href="{}" style="margin-right:10px">'
            '<i class="fa fa-file-text-o" aria-hidden="true"></i> Jawaban'
            '</a>',
            reverse("admin:sis_answer_change", args=(obj.id, )),
        )
    object_action.short_description = _("object action")


admin.site.register(Module, ModuleAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Report)
