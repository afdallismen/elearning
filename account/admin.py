from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from account.forms import MyAdminAuthenticationForm
from account.list_filter import (
    StudentProgramListFilter as filter_program,
    CredentialListFilter as filter_credential)
from account.models import Student, Lecturer
from account.utils import (
    MAHASISWA_CHANGE_LINK as link_mahasiswa,
    DOSEN_CHANGE_LINK as link_dosen,
    PENGGUNA_CHANGE_LINK as link_pengguna,
    DELETE_LINK as link_delete)


def activate_users(model_admin, request, queryset):
    queryset.update(is_active=True)
activate_users.short_description = _("Make selected users as active") # noqa


def deactivate_users(model_admin, request, queryset):
    queryset.update(is_active=False)
deactivate_users.short_description = _("Make selected users as inactive") # noqa


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
    full_name.short_description = _("full name")


class BaseAccountAdmin(admin.ModelAdmin):
    list_display_links = None
    search_fields = (
        '=user__username',
        '=user__first_name',
        '=user__last_name'
    )

    class Media:
        css = {
            'all': (
                "font-awesome-4.7.0/css/font-awesome.min.css",
            )
        }

    def name(self, obj):
        return obj.name
    name.short_description = _('user')
    name.admin_order_field = 'user__fist_name'

    def has_add_permission(self, obj):
        return False


class StudentAdmin(BaseAccountAdmin):
    list_display = ('nobp', 'name', 'class_of', 'in_semester',
                    'object_action')
    list_filter = (filter_program, )

    def class_of(self, obj):
        return obj.class_of
    class_of.short_description = _('class of')
    class_of.admin_order_field = 'nobp'

    def in_semester(self, obj):
        return obj.in_semester
    in_semester.short_description = _('in semester')
    in_semester.admin_order_field = 'nobp'

    def object_action(self, obj):
        return format_html(
            "".join((link_mahasiswa, link_pengguna, link_delete)),
            reverse("admin:account_student_change", args=(obj.pk, )),
            reverse("admin:auth_user_change", args=(obj.user.id, )),
            reverse("admin:auth_user_delete", args=(obj.user.id, )),
        )
    object_action.short_description = _("object action")


class LecturerAdmin(BaseAccountAdmin):
    list_display = ('nip', 'name', 'object_action')

    def object_action(self, obj):
        return format_html(
            "".join((link_dosen, link_pengguna, link_delete)),
            reverse("admin:account_lecturer_change", args=(obj.pk, )),
            reverse("admin:auth_user_change", args=(obj.user.id, )),
            reverse("admin:auth_user_delete", args=(obj.user.id, ))
        )
    object_action.short_description = _("object action")


admin.site.login_form = MyAdminAuthenticationForm

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Lecturer, LecturerAdmin)
