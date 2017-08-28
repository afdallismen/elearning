import nested_admin

from django.contrib import admin
from django.forms import modelformset_factory

from sis.forms import BaseQuestionFormSet
from sis.list_filters import AssignmentCategoryListFilter as filter_assignment
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
    the_title.short_description = "title"
    the_title.admin_order_field = 'title'

    def object_action(self, obj):
        return module_admin_object_action_link(obj)


class AssignmentAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    list_display = ('category', 'created_date', 'number_of_questions',
                    'object_action')
    list_display_links = None
    list_filter = (filter_assignment, )
    inlines = [QuestionInline]

    def number_of_questions(self, obj):
        return obj.question_set.count()
    number_of_questions.short_description = "number of questions"

    def object_action(self, obj):
        return assignment_admin_object_action_link(obj)


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


class AssignmentResultAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name')
    list_display = ('student', 'assignment', 'score')
    list_display_links = None
    list_filter = (filter_assignment,
                   ('student', admin.RelatedOnlyFieldListFilter), )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FinalResultAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name')
    list_display_links = None

    def __init__(self, *args, **kwargs):
        self.counters = {
            'weekly': 0,
            'mid': 0,
            'final': 0,
        }
        super(FinalResultAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        self.weekly_assignments = Assignment.objects.filter(
            category=0).order_by('created_date')

        self.mid_assignments = Assignment.objects.filter(
            category=1).order_by('created_date')

        self.final_assignments = Assignment.objects.filter(
            category=2).order_by('created_date')

        list_display = ['student', ]
        if self.weekly_assignments:
            list_display.extend(
                ['weekly' for assignment in self.weekly_assignments])
        if self.mid_assignments:
            list_display.extend(
                ['mid' for assignment in self.mid_assignments])
        if self.final_assignments:
            list_display.extend(
                ['final' for assignment in self.final_assignments])
        list_display.append('score')
        list_display.append('letter_value')

        return list_display

    def letter_value(self, obj):
        return obj.letter_value

    def weekly(self, obj):
        assignment_id = self.weekly_assignments[self.counters['weekly']].id
        try:
            score = AssignmentResult.objects.get(
                student=obj.student, assignment=assignment_id
            ).score
        except AssignmentResult.DoesNotExist:
            score = 0
        if self.counters['weekly'] < len(self.weekly_assignments) - 1:
            self.counters['weekly'] += 1
        else:
            self.counters['weekly'] = 0
        return score

    def mid(self, obj):
        assignment_id = self.mid_assignments[self.counters['mid']].id
        try:
            score = AssignmentResult.objects.get(
                student=obj.student, assignment=assignment_id
            ).score
        except AssignmentResult.DoesNotExist:
            score = 0
        if self.counters['mid'] < len(self.mid_assignments) - 1:
            self.counters['mid'] += 1
        else:
            self.counters['mid'] = 0
        return score

    def final(self, obj):
        assignment_id = self.final_assignments[self.counters['final']].id
        try:
            score = AssignmentResult.objects.get(
                student=obj.student, assignment=assignment_id
            ).score
        except AssignmentResult.DoesNotExist:
            score = 0
        if self.counters['final'] < len(self.final_assignments) - 1:
            self.counters['final'] += 1
        else:
            self.counters['final'] = 0
        return score

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Module, ModuleAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AssignmentResult, AssignmentResultAdmin)
admin.site.register(FinalResult, FinalResultAdmin)
