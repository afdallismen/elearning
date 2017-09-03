import nested_admin

from django.contrib import admin
from django.forms import modelformset_factory

from sis.forms import BaseQuestionFormSet
from sis.list_filters import AssignmentCategoryListFilter as filter_category
from sis.models import (
    Module, Answer, Attachment, Assignment, Question, AssignmentResult,
    FinalResult, FinalResultPercentage)
from sis.utils import answer_admin_object_action_link


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
    readonly_fields = ['preview']

    def preview(self, instance):
        return instance.html_display


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [AttachmentInline]
    extra = 0
    formset = modelformset_factory(
        Question, fields=("__all__"), formset=BaseQuestionFormSet)


class ModuleAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    list_display = ('the_title', 'created_date', 'updated_date',
                    'number_of_attachments')
    search_fields = ('title', )
    inlines = [AttachmentInline]

    def the_title(self, obj):
        return obj.title
    the_title.short_description = "module"
    the_title.admin_order_field = 'title'

    def number_of_attachments(self, obj):
        return obj.attachments.count()


class AssignmentAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    list_display = ('cat', 'created_date', 'number_of_questions')
    list_filter = (filter_category, )
    inlines = [QuestionInline]

    def number_of_questions(self, obj):
        return obj.question_set.count()

    def cat(self, obj):
        return obj.get_category_display()
    cat.short_description = "assignment"
    cat.admin_order_field = 'category'


class AnswerAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    search_fields = (
        'student__user__username',
        'student__user__first_name',
        'student__user__last_name')
    list_filter = (filter_category,
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
    list_filter = (filter_category,
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
            'quiz': 0,
            'mid': 0,
            'final': 0,
        }
        super(FinalResultAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        self.assignments = {
            'quiz': Assignment.objects.filter(category=0).order_by(
                'created_date'),
            'mid': Assignment.objects.filter(category=1).order_by(
                'created_date'),
            'final': Assignment.objects.filter(category=2).order_by(
                'created_date')
        }
        list_display = ['student', ]
        count = (
            ('quiz', len(self.assignments['quiz'])),
            ('mid', len(self.assignments['mid'])),
            ('final', len(self.assignments['final']))
        )
        for ct in count:
            for _ in range(0, ct[1]):
                list_display.append(ct[0])
        list_display.append('score')
        list_display.append('letter_value')

        return list_display

    def letter_value(self, obj):
        return obj.letter_value

    def quiz(self, obj):
        return self._get_score_display(cat='quiz', obj=obj)

    def mid(self, obj):
        return self._get_score_display(cat='mid', obj=obj)

    def final(self, obj):
        return self._get_score_display(cat='final', obj=obj)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _get_score_display(self, cat, obj):
        assignment_id = self.assignments[cat][self.counters[cat]].id
        try:
            score = AssignmentResult.objects.get(
                student=obj.student, assignment=assignment_id
            ).score
        except AssignmentResult.DoesNotExist:
            score = "-"
        if self.counters[cat] < len(self.assignments[cat]) - 1:
            self.counters[cat] += 1
        else:
            self.counters[cat] = 0
        return score


class FinalResultPercentageAdmin(nested_admin.NestedModelAdmin):
    actions = None
    list_display_links = None
    list_display = ('quiz', 'mid', 'final')
    list_editable = ['quiz', 'mid', 'final']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Module, ModuleAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AssignmentResult, AssignmentResultAdmin)
admin.site.register(FinalResult, FinalResultAdmin)
admin.site.register(FinalResultPercentage, FinalResultPercentageAdmin)
