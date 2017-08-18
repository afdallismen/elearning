from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from account.forms import MyAdminAuthenticationForm
from account.list_filter import (
    StudentProgramListFilter as filter_program,
    CredentialListFilter as filter_credential)
from account.models import Student, Lecturer


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
    list_display = ('nobp', 'name', 'class_of', 'in_semester',
                    'object_action')
    list_display_links = None
    list_filter = (filter_program, )
    search_fields = ('=nobp', '=user__username', '=user__first_name', '=user__last_name')

    def name(self, obj):
        return str(obj).title()
    name.admin_order_field = 'user__first_name'

    def object_action(self, obj):
        html = '''
            <a href="{}" style="margin-right:10px">
                <i class="fa fa-vcard-o" aria-hidden="true"></i> Student
            </a>
            <a href="{}" style="margin-right:10px">
                <i class="fa fa-user-circle-o" aria-hidden="true"></i> User
            </a>
            <a href="{}">
                <i class="fa fa-times" aria-hidden="true"></i> Delete
            </a>'''

        return format_html(
            html,
            reverse("admin:account_student_change", args=(obj.pk, )),
            reverse("admin:auth_user_change", args=(obj.user.id, )),
            reverse("admin:auth_user_delete", args=(obj.user.id, ))
        )

    class Media:
        css = {
            'all': (
                "account/font-awesome-4.7.0/css/font-awesome.min.css",
            )
        }


class LecturerAdmin(admin.ModelAdmin):
    list_display = ('nip', 'name', 'object_action')
    list_display_links = None
    search_fields = ('=nip', '=user__username', '=user__first_name', '=user__last_name')

    def name(self, obj):
        return str(obj).title()
    name.admin_order_field = 'user__first_name'

    def object_action(self, obj):
        html = '''
            <a href="{}" style="margin-right:10px">
                <i class="fa fa-vcard-o" aria-hidden="true"></i> Lecturer
            </a>
            <a href="{}" style="margin-right:10px">
                <i class="fa fa-user-circle-o" aria-hidden="true"></i> User
            </a>
            <a href="{}">
                <i class="fa fa-times" aria-hidden="true"></i> Delete
            </a>'''

        return format_html(
            html,
            reverse("admin:account_lecturer_change", args=(obj.pk, )),
            reverse("admin:auth_user_change", args=(obj.user.id, )),
            reverse("admin:auth_user_delete", args=(obj.user.id, ))
        )

    class Media:
        css = {
            'all': (
                "account/font-awesome-4.7.0/css/font-awesome.min.css",
            )
        }


admin.site.login_form = MyAdminAuthenticationForm

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Lecturer, LecturerAdmin)
