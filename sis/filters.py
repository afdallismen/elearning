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