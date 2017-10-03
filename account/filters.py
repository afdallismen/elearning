from operator import itemgetter

from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _

from account.models import Student


class GroupListFilter(admin.SimpleListFilter):
    title = _("group")
    parameter_name = "group"

    def lookups(self, request, model_admin):
        objs = Group.objects.all()
        return ((group.name, _(group.name).title()) for group in objs)

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(groups__name=self.value())
        return queryset


class StudentSemesterListFilter(admin.SimpleListFilter):
    title = _("semester")
    parameter_name = "semester"

    def lookups(self, request, model_admin):
        students = Student.objects.all()
        objs = []
        for student in students:
            year = student.nobp
            exist = False
            for obj in objs:
                if obj['year'] == year:
                    exist = True
            if not exist:
                objs.append(
                    {'year': student.nobp[0:2], 'semester': student.semester})
        objs = sorted(objs, key=itemgetter('semester'), reverse=True)
        return ((obj['year'], obj['semester']) for obj in objs)

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(student__nobp__startswith=self.value())
        return queryset
