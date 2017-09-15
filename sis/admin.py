import nested_admin

from django.contrib import admin
from django.forms import modelformset_factory
from django.utils.translation import ugettext as _

from sis.forms import BaseQuestionFormSet
from sis.filters import AssignmentCategoryListFilter as filter_category
from sis.models import (
    Module, Answer, Attachment, Assignment, Question, AssignmentResult,
    FinalResult, FinalResultPercentage)
from sis.utils import answer_admin_change_link


class SisAdminMixin(object):
    class Media:
        css = {'all': ("font-awesome-4.7.0/css/font-awesome.min.css", )}


class AttachmentInline(nested_admin.NestedGenericStackedInline):
    model = Attachment
    extra = 0
    readonly_fields = ['preview']

    def preview(self, instance):
        return instance.html_display
    preview.short_description = ""


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [AttachmentInline]
    extra = 0
    formset = modelformset_factory(Question,
                                   fields=("__all__"),
                                   formset=BaseQuestionFormSet)


class ModuleAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title', 'created_date', 'updated_date',
                    'number_of_attachments')
    search_fields = ('title', )
    inlines = [AttachmentInline]

    def number_of_attachments(self, obj):
        return obj.attachments.count()
    number_of_attachments.short_description = _("number of attachments")


class AssignmentAdmin(nested_admin.NestedModelAdmin):
    list_display = ('category', 'created_date', 'number_of_questions')
    list_filter = (filter_category, )
    inlines = [QuestionInline]

    def number_of_questions(self, obj):
        return obj.question_set.count()
    number_of_questions.short_description = _("number of questions")


class AnswerAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    search_fields = ('student__user__username',
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
    assignment.short_description = _("assignment")

    def score_percentage(self, obj):
        return obj.question.score_percentage
    score_percentage.short_description = _("score percentage")

    def object_action(self, obj):
        return answer_admin_change_link(pk=obj.pk)
    object_action.short_description = _("object action")


class AssignmentResultAdmin(nested_admin.NestedModelAdmin):
    search_fields = ('student__user__username',
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


class FinalResultAdmin(nested_admin.NestedModelAdmin):
    search_fields = ('student__user__username',
                     'student__user__first_name',
                     'student__user__last_name')
    list_display_links = None

    def __init__(self, *args, **kwargs):
        self.counters = {'quiz': 0,
                         'mid': 0,
                         'final': 0}
        super(FinalResultAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        # Get all assignments per category
        assignment_objects = Assignment.objects.order_by('created_date')
        self.assignments = {'quiz': assignment_objects.filter(category=0),
                            'mid': assignment_objects.filter(category=1),
                            'final': assignment_objects.filter(category=2)}

        list_display = ['student', ]  # Initial list display

        # Get count of each category
        count = (('quiz', len(self.assignments['quiz'])),
                 ('mid', len(self.assignments['mid'])),
                 ('final', len(self.assignments['final'])))

        # Generate list display
        for ct in count:
            # Append key to list display for each count
            for ign in range(0, ct[1]):
                list_display.append(ct[0])

        # Rest of the list display
        list_display.extend(["score", "letter_value"])

        return list_display

    def letter_value(self, obj):
        return obj.letter_value
    letter_value.short_description = _("letter value")

    def _raise_counter(self, cat):
        if self.counters[cat] < len(self.assignments[cat]) - 1:
            self.counters[cat] += 1
        else:
            self.counters[cat] = 0

    def quiz(self, obj):
        assignment = self.assignments['quiz'][self.counters['quiz']].pk
        score = AssignmentResult.objects.get_score(student=obj.student,
                                                   assignment=assignment)
        self._raise_counter('quiz')
        return score
    quiz.short_description = _("quiz")

    def mid(self, obj):
        assignment = self.assignments['mid'][self.counters['mid']].pk
        score = AssignmentResult.objects.get_score(student=obj.student,
                                                   assignment=assignment)
        self._raise_counter('mid')
        return score
    mid.short_description = _("mid")

    def final(self, obj):
        assignment = self.assignments['final'][self.counters['final']].pk
        score = AssignmentResult.objects.get_score(student=obj.student,
                                                   assignment=assignment)
        self._raise_counter('final')
        return score
    final.short_description = _("final")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
