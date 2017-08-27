import nested_admin

from django.contrib import admin
from django.utils.translation import ugettext as _
from django.forms import modelformset_factory

from sis.forms import BaseQuestionFormSet
from sis.list_filters import (
    AssignmentCategoryListFilter as filter_assignment,
    AssignmentActiveListFilter as filter_active)
from sis.models import (
    Module, Answer, Attachment, Assignment, Question, AssignmentResult,
    FinalResult)
from sis.utils import (
    module_admin_object_action_link, assignment_admin_object_action_link,
    answer_admin_object_action_link)


class SisAdminMixin(object):
    class Media:
        css = {
            'all': (
                "font-awesome-4.7.0/css/font-awesome.min.css",
            )
        }

    def object_action(self, obj):
        pass


class AttachmentInline(nested_admin.NestedGenericStackedInline):
    model = Attachment
    extra = 0


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [AttachmentInline]
    extra = 0
    formset = modelformset_factory(
        Question, fields=("__all__"), formset=BaseQuestionFormSet)


class ModuleAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    list_display = ('the_title', 'created_date', 'updated_date',
                    'object_action')
    list_display_links = None
    search_fields = ('title', )
    inlines = [AttachmentInline]

    def the_title(self, obj):
        return (obj.title).title()
    the_title.short_description = _("title")
    the_title.admin_order_field = 'title'

    def object_action(self, obj):
        return module_admin_object_action_link(obj)
    object_action.short_description = _("object action")


class AssignmentAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    list_display = ('category', 'created_date', 'number_of_questions',
                    'object_action')
    list_display_links = None
    list_filter = (filter_assignment, )
    inlines = [QuestionInline]

    def number_of_questions(self, obj):
        return obj.question_set.count()
    number_of_questions.short_description = _("number of questions")

    def object_action(self, obj):
        return assignment_admin_object_action_link(obj)
    object_action.short_description = _("object action")


class AnswerAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name')
    list_filter = (filter_assignment,
                   ('student', admin.RelatedOnlyFieldListFilter))
    list_display = ('student', 'assignment', 'question', 'score_percentage',
                    'score', 'object_action')
    list_display_links = None
    inlines = [AttachmentInline]

    def assignment(self, obj):
        return obj.question.assignment

    def score_percentage(self, obj):
        return obj.question.score_percentage

    def object_action(self, obj):
        return answer_admin_object_action_link(obj)
    object_action.short_description = _("object action")


class AssignmentResultAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name')
    list_display = ('student', 'assignment', 'score')
    list_display_links = None
    list_filters = (('student', admin.RelatedOnlyFieldListFilter), )


admin.site.register(Module, ModuleAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AssignmentResult, AssignmentResultAdmin)
admin.site.register(FinalResult)
