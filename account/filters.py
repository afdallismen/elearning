from operator import itemgetter

from django.contrib import admin
from django.utils.translation import ugettext as _, ugettext_lazy as _lazy

from account.models import Student, Lecturer


class UserIdentityListFilter(admin.SimpleListFilter):
    title = _("group")
    parameter_name = "group"

    def lookups(self, request, model_admin):
        objs = [
            (Student._meta.object_name, _lazy(Student._meta.object_name)),
            (Lecturer._meta.object_name, _lazy(Lecturer._meta.object_name))
        ]
        return ((obj[0], obj[1].title()) for obj in objs)

    def queryset(self, request, queryset):
        if self.value():
            lookup = {
                Student._meta.object_name: False,
                Lecturer._meta.object_name: True
            }
            queryset = queryset.filter(is_staff=lookup[self.value()])
        return queryset


class StudentSemesterListFilter(admin.SimpleListFilter):
    title = _("semester")
    parameter_name = "semester"

    def lookups(self, request, model_admin):
        students = Student.objects.all()
        objs = []
        for student in students:
            year = student.nobp  # CHECK THIS !
            exist = False
            for obj in objs:
                if obj['year'] == year:
                    exist = True
            if not exist:
                objs.append({
                    'year': student.nobp[0:2],
                    'semester': student.semester
                })
        objs = sorted(objs, key=itemgetter('semester'), reverse=True)
        return ((obj['year'], obj['semester']) for obj in objs)

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(student__nobp__startswith=self.value())
        return queryset
