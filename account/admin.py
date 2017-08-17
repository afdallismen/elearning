from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from account.list_filter import (
    StudentProgramListFilter as filter_program,
    CredentialListFilter as filter_credential)
from account.models import Student


def activate_users(model_admin, request, queryset):
    queryset.update(is_active=True)
activate_users.short_description = "Make selected users as active" # noqa


def deactivate_users(model_admin, request, queryset):
    queryset.update(is_active=False)
deactivate_users.short_description = "Make selected users as inactive" # noqa


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    actions = (activate_users, deactivate_users)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        (None, {'fields': ('groups', )})
    )
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('full_name', 'email', 'date_joined', 'is_active')
    list_filter = ('is_active', filter_credential)
    readonly_fields = ('last_login', 'date_joined')

    def full_name(self, obj):
        return " ".join((obj.first_name, obj.last_name)).title()


class StudentAdmin(admin.ModelAdmin):
    action = ()
    list_display = ('full_name', 'nobp', 'class_of', 'in_semester')
    list_filter = (filter_program, )

    def full_name(self, obj):
        return str(obj).title()

    def semester(self, obj):
        return obj.in_semester


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
