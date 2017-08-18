from django.contrib import admin
from django.utils.translation import ugettext as _


class StudentProgramListFilter(admin.SimpleListFilter):
    title = _("program")
    parameter_name = "program"

    def lookups(self, request, model_admin):
        return (
            ('000', _('Computer System')),
            ('100', _('Information System'))
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                nobp__regex=r'^[0-9]{{2}}{}[0-9]{{2}}$'.format(
                    self.value()
                )
            )
        return queryset


class CredentialListFilter(admin.SimpleListFilter):
    title = _("credential")
    parameter_name = "cred"

    def lookups(self, request, model_admin):
        return (
            ('student', _('student').title()),
            ('lecturer', _('lecturer').title()),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(groups__name=self.value())
        return queryset
