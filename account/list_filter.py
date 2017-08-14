from django.contrib import admin


class StudentClassListFilter(admin.SimpleListFilter):
    title = "class"
    parameter_name = "class_of"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        avaible_class = set()
        for user in qs:
            avaible_class.add(user.student.class_of)
        avaible_class = sorted(avaible_class, reverse=True)

        return tuple(
            (class_of, class_of) for class_of in avaible_class
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                student__nobp__regex=r'^{}[0-9]{{5}}$'.format(
                    self.value()[-2:]
                )
            )
        return queryset


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
                student__nobp__regex=r'^[0-9]{{2}}{}[0-9]{{2}}$'.format(
                    self.value()
                )
            )
        return queryset
