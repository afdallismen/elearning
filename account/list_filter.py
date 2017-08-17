from django.contrib import admin


class StudentProgramListFilter(admin.SimpleListFilter):
    title = "program"
    parameter_name = "program"

    def lookups(self, request, model_admin):
        return (
            ('000', 'Computer System'),
            ('100', 'Information System')
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
    title = "credential"
    parameter_name = "cred"

    def lookups(self, request, model_admin):
        return (
            ('student', 'Student'),
            ('lecturer', 'Lecturer'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(groups__name=self.value())
        return queryset
