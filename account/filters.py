from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _


class GroupListFilter(admin.SimpleListFilter):
    title = _("group")
    parameter_name = "group"

    def lookups(self, request, model_admin):
        objs = Group.objects.all()
        return ((group.name, _(group.name)) for group in objs)

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(groups__name=self.value)
        return queryset
