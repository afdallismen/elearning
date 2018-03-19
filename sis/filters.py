from django.contrib import admin
from django.utils.translation import ugettext as _

from sis.models import Assignment, Answer, AssignmentResult


class AssignmentCategoryListFilter(admin.SimpleListFilter):
    title = _("assignment cateory")
    parameter_name = "cat"

    def __init__(self, request, params, model, model_admin):
        self.model = model
        super(AssignmentCategoryListFilter, self).__init__(request, params, model, model_admin)  # noqa

    def lookups(self, request, model_admin):
        if self.model.objects.count():
            return Assignment.CATEGORY_CHOICES
        return None

    def queryset(self, request, queryset):
        if self.value():
            if self.model == Assignment:
                queryset = queryset.filter(category=self.value())
            elif self.model == Answer:
                queryset = queryset.filter(
                    question__assignment__category=self.value()
                )
            elif self.model == AssignmentResult:
                queryset = queryset.filter(
                    assignment__category=self.value()
                )
        return queryset


class AnswerHasExaminedListFilter(admin.SimpleListFilter):
    title = _("has been examined")
    parameter_name = "examined"

    def lookups(self, request, model_admin):
        objs = [
            {'key': _("True"), 'value': True},
            {'key': _("False"), 'value': False}
        ]
        return ((obj['value'], obj['key']) for obj in objs)

    def queryset(self, request, queryset):
        answers = Answer.objects.all()
        examined = [answer for answer in answers if answer.has_examined]
        examined_pks = [answer.pk for answer in examined]
        if self.value() is not None and self.value() == "True":
            return queryset.filter(pk__in=examined_pks)
        elif self.value() is not None and self.value() == "False":
            return queryset.exclude(pk__in=examined_pks)
        elif self.value() is None:
            return queryset
