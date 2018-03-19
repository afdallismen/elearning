import nested_admin

from django.contrib import admin
from django.forms import modelformset_factory
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from main.templatetags.mytags import letter
from sis.actions import print_students_result
from sis.forms import BaseQuestionFormSet
from sis.filters import (
    AssignmentCategoryListFilter as filter_category,
    AnswerHasExaminedListFilter as filter_examined,
)
from sis.models import (
    Module, Answer, Attachment, Assignment, Question, AssignmentResult,
    FinalResult, FinalResultPercentage, Course
)
from main.utils import object_link


class SisAdminMixin(object):
    class Media:
        css = {'all': ("font-awesome-4.7.0/css/font-awesome.min.css", )}


class AttachmentInline(nested_admin.NestedGenericStackedInline):
    model = Attachment
    extra = 0
    readonly_fields = ['preview']

    def preview(self, obj):
        return obj.admin_display
    preview.short_description = _("preview")


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [AttachmentInline]
    extra = 0
    formset = modelformset_factory(
        Question,
        fields=('__all__'),
        formset=BaseQuestionFormSet
    )


class ModuleAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title_display', 'created_on', 'number_of_attachments')
    list_filter = ('courses', 'created_on', )
    search_fields = ('title', )
    inlines = [AttachmentInline]

    def title_display(self, obj):
        return obj.title.title()
    title_display.short_description = _("title")

    def number_of_attachments(self, obj):
        return obj.attachments.count()
    number_of_attachments.short_description = _("number of attachments")


class AssignmentAdmin(nested_admin.NestedModelAdmin):
    empty_value_display = "-"
    list_display = ('category_display', 'short_description_display', 'due',
                    'published', 'active', 'action')
    list_display_links = None
    list_filter = (filter_category, 'courses', 'due')
    inlines = [QuestionInline]

    def category_display(self, obj):
        return obj.get_category_display().title()
    category_display.short_description = _("category")
    category_display.admin_order_field = 'category'

    def short_description_display(self, obj):
        return obj.short_description.capitalize() or self.empty_value_display
    short_description_display.short_description = _("short description")
    short_description_display.admin_order_field = 'short_description'

    def published(self, obj):
        return bool(obj.status)
    published.short_description = _("published")
    published.admin_order_field = 'status'
    published.boolean = True

    def active(self, obj):
        return not obj.has_expired
    active.short_description = _("active")
    active.boolean = True

    def action(self, obj):
        return object_link(
            'admin:sis_assignment_change',
            "Edit",
            obj.pk
        )
    action.short_description = _("action")


class AnswerAdmin(nested_admin.NestedModelAdmin, SisAdminMixin):
    fields = ['text', 'score']
    readonly_fields = ['text']
    search_fields = ('student__user__username',
                     'student__user__first_name',
                     'student__user__last_name',
                     'student__nobp')
    list_filter = (filter_category, filter_examined,
                   ('student', admin.RelatedOnlyFieldListFilter))
    list_display = ('name_display', 'nobp_display', 'assignment_display',
                    'question_display', 'score_percentage_display', 'score',
                    'has_examined_display', 'action')
    list_display_links = None
    inlines = [AttachmentInline]

    def has_add_permission(self, request):
        return False

    def name_display(self, obj):
        return object_link(
            'admin:account_myuser_change',
            obj.student.user.name.title(),
            obj.student.user.pk
        )
    name_display.short_description = _("name")
    name_display.admin_order_field = 'student__user'

    def nobp_display(self, obj):
        return object_link(
            'admin:account_student_change',
            obj.student.nobp,
            obj.student.pk
        )
    nobp_display.short_description = 'no.bp'
    nobp_display.admin_order_field = 'student__nobp'

    def question_display(self, obj):
        return str(obj.question).capitalize()
    question_display.short_description = _("question")

    def assignment_display(self, obj):
        return object_link(
            'admin:sis_assignment_change',
            str(obj.question.assignment).title(),
            obj.question.assignment.pk
        )
    assignment_display.short_description = _("assignment")
    assignment_display.admin_order_field = 'question__assignment'

    def score_percentage_display(self, obj):
        return obj.question.score_percentage
    score_percentage_display.short_description = _("score percentage (%)")
    score_percentage_display.admin_order_field = 'question__score_percentage'

    def has_examined_display(self, obj):
        return obj.has_examined
    has_examined_display.short_description = _("has been examined")
    has_examined_display.boolean = True

    def action(self, obj):
        return object_link(
            'admin:sis_answer_change',
            "Check",
            obj.pk
        )
    action.short_description = _("action")


class AssignmentResultAdmin(nested_admin.NestedModelAdmin):
    search_fields = ('student__user__username', 'student__user__first_name',
                     'student__user__last_name', 'student_nobp')
    list_display = ('name_display', 'nobp_display', 'assignment_display',
                    'score', 'letter_score_display')
    list_display_links = None
    list_filter = (filter_category,
                   ('student', admin.RelatedOnlyFieldListFilter), )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def name_display(self, obj):
        return object_link(
            'admin:account_myuser_change',
            obj.student.user.name.title(),
            obj.student.user.pk
        )
    name_display.short_description = _("name")
    name_display.admin_order_field = 'student__user__username'

    def nobp_display(self, obj):
        return object_link(
            'admin:account_student_change',
            obj.student.nobp,
            obj.student.pk
        )
    nobp_display.short_description = "no.bp"
    nobp_display.admin_order_field = 'student__nobp'

    def assignment_display(self, obj):
        return object_link(
            'admin:sis_assignment_change',
            str(obj.assignment).title(),
            obj.assignment.pk
        )
    assignment_display.short_description = _("assignment")
    assignment_display.admin_order_field = 'assignment__category'

    def letter_score_display(self, obj):
        return letter(obj.score)
    letter_score_display.short_description = _("letter score")
    letter_score_display.admin_order_field = 'score'


class FinalResultAdmin(nested_admin.NestedModelAdmin):
    actions = (print_students_result, )
    list_filter = ('student__belong_in', )
    search_fields = ('student__user__username', 'student__user__first_name',
                     'student__user__last_name', 'student_nobp')
    list_display_links = None

    def __init__(self, *args, **kwargs):
        self.counters = {
            'exercise': 0,
            'quiz': 0,
            'mid': 0,
            'final': 0
        }
        super(FinalResultAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        # Get all assignments per category
        assignment_objects = Assignment.objects.order_by('created_on')
        self.assignments = {
            'exercise': assignment_objects.filter(category=0),
            'quiz': assignment_objects.filter(category=1),
            'mid': assignment_objects.filter(category=2),
            'final': assignment_objects.filter(category=3)
        }

        list_display = ['name_display', 'nobp_display', 'class_display']  # noqa

        # Get count of each category
        count = (
            ('exercise', len(self.assignments['exercise'])),
            ('quiz', len(self.assignments['quiz'])),
            ('mid', len(self.assignments['mid'])),
            ('final', len(self.assignments['final']))
        )

        # Generate list display
        for ct in count:
            # Append key to list display for each count
            for ign in range(0, ct[1]):
                list_display.append(ct[0])

        # Rest of the list display
        list_display.extend(["score", "letter_score_display"])

        return list_display

    def _raise_counter(self, cat):
        if self.counters[cat] < len(self.assignments[cat]) - 1:
            self.counters[cat] += 1
        else:
            self.counters[cat] = 0

    def exercise(self, obj):
        assignment = self.assignments['exercise'][self.counters['exercise']].pk
        exist = AssignmentResult.objects.filter(
            student=obj.student,
            assignment=assignment
        )
        self._raise_counter('exercise')
        if not exist:
            return "-"
        score = AssignmentResult.objects.get_score(
            student=obj.student,
            assignment=assignment
        )
        return score
    exercise.short_description = _("exercise")

    def quiz(self, obj):
        assignment = self.assignments['quiz'][self.counters['quiz']].pk
        exist = AssignmentResult.objects.filter(
            student=obj.student,
            assignment=assignment
        )
        self._raise_counter('quiz')
        if not exist:
            return "-"
        score = AssignmentResult.objects.get_score(
            student=obj.student,
            assignment=assignment
        )
        return score
    quiz.short_description = _("quiz")

    def mid(self, obj):
        assignment = self.assignments['mid'][self.counters['mid']].pk
        exist = AssignmentResult.objects.filter(
            student=obj.student,
            assignment=assignment
        )
        self._raise_counter('mid')
        if not exist:
            return "-"
        score = AssignmentResult.objects.get_score(
            student=obj.student,
            assignment=assignment
        )
        return score
    mid.short_description = _("mid")

    def final(self, obj):
        assignment = self.assignments['final'][self.counters['final']].pk
        exist = AssignmentResult.objects.filter(
            student=obj.student,
            assignment=assignment
        )
        self._raise_counter('final')
        if not exist:
            return "-"
        score = AssignmentResult.objects.get_score(
            student=obj.student,
            assignment=assignment
        )
        return score
    final.short_description = _("final")

    def name_display(self, obj):
        return object_link(
            "admin:account_myuser_change",
            obj.student.user.name.title(),
            obj.student.user.pk
        )
    name_display.short_description = _("name")
    name_display.admin_order_field = 'student__user_name'

    def nobp_display(self, obj):
        return object_link(
            "admin:account_student_change",
            obj.student.nobp,
            obj.student.pk
        )
    nobp_display.short_description = _("nobp")
    nobp_display.admin_order_field = 'student_nobp'

    def class_display(self, obj):
        return obj.student.belong_in.name.title()
    class_display.short_description = _("class")
    class_display.admin_order_field = 'student_belong_in'

    def letter_score_display(self, obj):
        return letter(obj.score)
    letter_score_display.short_description = _("letter score")

    def action(self, obj):
        return format_html(
            "<a href='http://localhost:8000/admin/sis/assignmentresult/?o=3&student__id__exact={}'>Detail</a>",  # noqa
            obj.student.pk
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FinalResultPercentageAdmin(nested_admin.NestedModelAdmin):
    actions = None
    list_display_links = None
    list_display = ('exercise', 'quiz', 'mid', 'final')
    list_editable = ('exercise', 'quiz', 'mid', 'final')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CourseAdmin(nested_admin.NestedModelAdmin):
    empty_value_display = "-"
    list_display_links = None
    list_display = ('name_display', 'student_count_display', 'capacity')

    def name_display(self, obj):
        return object_link(
            "admin:sis_course_change",
            obj.name.title(),
            obj.pk
        )
    name_display.short_description = _("name")
    name_display.admin_order_field = 'name'

    def student_count_display(self, obj):
        count = obj.student_set.count()
        if count > 0:
            return format_html(
                "<a href='http://localhost:8000/admin/account/myuser"
                "/?student__belong_in__id__exact={}'>{}</a>",
                obj.pk,
                count
            )
        return self.empty_value_display
    student_count_display.short_description = _("current student count")


admin.site.register(Answer, AnswerAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentResult, AssignmentResultAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(FinalResult, FinalResultAdmin)
admin.site.register(FinalResultPercentage, FinalResultPercentageAdmin)
admin.site.register(Module, ModuleAdmin)
