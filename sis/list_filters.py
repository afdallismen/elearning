import datetime

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext as _

from sis.models import Assignment, Module, Answer


def _get_academic_year_lookups(model):
    if model in [Answer, Assignment]:
        lookups_model = Assignment
    elif model == Module:
        lookups_model = Module

    dates = list(lookups_model.objects.dates(
        'created_date', 'year', order='DESC'))
    if dates:
        least_year = dates[len(dates) - 1].year
        dates.append(datetime.date(least_year - 1, 1, 1))

        return (
            (date.year, "{}/{}".format(date.year, date.year + 1))
            for date in dates
        )
    else:
        return None


def _get_academic_year_queryset(model, queryset, value):
    if model == Answer:
        return queryset.filter(
            question__assignment__created_date__year=str(value)
        )
    elif model in [Assignment, Module]:
        return queryset.filter(
            created_date__year=str(value)
        )


def _get_semester_queryset(model, queryset, value):
    if model == Answer:
        semester = {
            'odd': queryset.filter(
                question__assignment__created_date__month__gte=6
            ),
            'even': queryset.filter(
                question__assignment__created_date__month__lte=6
            )
        }
    elif model in [Assignment, Module]:
        semester = {
            'odd': queryset.filter(
                created_date__month__gte=6
            ),
            'even': queryset.filter(
                created_date__month__lte=6
            )
        }

    return semester[value]


class AcademicYearListFilter(admin.SimpleListFilter):
    title = _("academic year")
    parameter_name = 'year'

    def __init__(self, request, params, model, model_admin):
        self.model = model
        super(AcademicYearListFilter, self).__init__(request, params, model,
                                                     model_admin)

    def lookups(self, request, model_admin):
        return _get_academic_year_lookups(self.model)

    def queryset(self, request, queryset):
        if self.value():
            return _get_academic_year_queryset(
                self.model, queryset, self.value())
        return queryset


class SemesterListFilter(admin.SimpleListFilter):
    title = _("semester")
    parameter_name = 'semester'

    def __init__(self, request, params, model, model_admin):
        self.model = model
        super(SemesterListFilter, self).__init__(request, params, model,
                                                 model_admin)

    def lookups(self, request, model_admin):
        return (
            ('odd', _("odd").title()),
            ('even', _("even").title())
        )

    def queryset(self, request, queryset):
        if self.value():
            return _get_semester_queryset(self.model, queryset, self.value())
        return queryset


class ModuleTitleListFilter(admin.SimpleListFilter):
    title = _("module")
    parameter_name = 'module'

    def lookups(self, request, model_admin):
        modules = Module.objects.values('slug', 'title')

        return (
            (module['slug'], module['title']) for module in modules
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                question__assignment__module__slug=self.value()
            )
        return queryset


class AssignmentCategoryListFilter(admin.SimpleListFilter):
    title = _("assignment cateory")
    parameter_name = 'cat'

    def lookups(self, request, model_admin):
        return Assignment.ASSIGNMENT_CATEGORY_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                question__assignment__category=self.value()
            )
        return queryset


class AssignmentActiveListFilter(admin.SimpleListFilter):
    title = _("active")
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ("active", _("active")),
            ("not_active", _("not active"))
        )

    def queryset(self, request, queryset):
        if self.value():
            now = timezone.now().date()
            qs = dict()
            qs['active'] = queryset.filter(due_date__gte=now)
            qs['not_active'] = queryset.filter(due_date__lte=now)
            return qs[self.value()]
        return queryset
