from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from account.list_filter import (
    StudentClassListFilter as filter_class,
    StudentProgramListFilter as filter_program)
from account.models import Student


User._meta.verbose_name = "Student"
User._meta.verbose_name_plural = "Students"


def activate_users(model_admin, request, queryset):
    queryset.update(is_active=True)
activate_users.short_description = "Make selected users as active" # noqa


def deactivate_users(model_admin, request, queryset):
    queryset.update(is_active=False)
deactivate_users.short_description = "Make selected users as inactive" # noqa


class StudentInline(admin.StackedInline):
    can_delete = False
    model = Student
    template = 'admin/edit_inline/stacked.html'
    verbose_name_plural = 'extra info'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    actions = (activate_users, deactivate_users)
    inlines = (StudentInline, )
    list_display = ('student_nobp', 'student_name', 'email', 'is_active')
    list_display_links = ('student_nobp', 'student_name', )
    list_filter = (filter_class, filter_program)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
    )

    def student_name(self, obj):
        return str(obj.student)
    student_name.admin_order_field = 'first_name'
    student_name.short_description = 'Name'

    def student_nobp(self, obj):
        return str(obj.student.nobp)
    student_nobp.admin_order_field = 'student__nobp'
    student_nobp.short_description = 'No. BP'

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        return qs.filter(is_staff=False)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
