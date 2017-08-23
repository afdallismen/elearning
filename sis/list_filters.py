import datetime
from django.contrib import admin
from django.utils.translation import ugettext as _

from sis.models import Assignment, Module


class AcademicYearListFilter(admin.SimpleListFilter):
    title = _("academic year")
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        dates = list(Assignment.objects.dates(
            'created_date', 'year', order='DESC'))
        least_year = dates[len(dates) - 1].year
        dates.append(datetime.date(least_year - 1, 1, 1))

        return (
            (date.year, "{}/{}".format(date.year, date.year + 1))
            for date in dates
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                question__assignment__created_date__year=str(self.value())
            )
        return queryset


class SemesterListFilter(admin.SimpleListFilter):
    title = _("semester")
    parameter_name = 'semester'

    def lookups(self, request, model_admin):
        return (
            ('odd', _("odd").title()),
            ('even', _("even").title())
        )

    def queryset(self, request, queryset):
        if self.value():
            semester = {
                'odd': queryset.filter(
                    question__assignment__created_date__month__gte=6
                ),
                'even': queryset.filter(
                    question__assignment__created_date__month__lte=6
                )
            }
            return semester[self.value()]
        return queryset


class ModuleListFilter(admin.SimpleListFilter):
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


class AssignmentTypeListFilter(admin.SimpleListFilter):
    title = _("assignment type")
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return Assignment.ASSIGNMENT_TYPE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                question__assignment__assignment_type=self.value()
            )
        return queryset
