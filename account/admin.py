from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html

from account.models import Student, Lecturer, MyUser


def activate_users(model_admin, request, queryset):
    for user in queryset:
        if hasattr(user, 'student') or hasattr(user, 'lecturer'):
            queryset.update(is_active=True)
activate_users.short_description = "Make selected users as active" # noqa


def deactivate_users(model_admin, request, queryset):
    queryset.update(is_active=False)
deactivate_users.short_description = "Make selected users as inactive" # noqa


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    empty_value_display = "-"
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
    list_display = ('__str__', 'email', 'identity', 'is_active')
    list_filter = ('is_active', 'groups')

    def identity(self, obj):
        if not any([hasattr(obj, 'student'), hasattr(obj, 'lecturer')]):
            return self.empty_value_display
        if hasattr(obj, 'student') and obj.student is not None:
            link = reverse("admin:account_student_change",
                           args=(obj.student.id, ))
            num = obj.student.nobp
        elif hasattr(obj, 'lecturer') and obj.lecturer is not None:
            link = reverse("admin:account_lecturer_change",
                           args=(obj.lecturer.id, ))
            num = obj.lecturer.nip
        return format_html("<a href={}><b>{}</b></a>", link, num)


class NoModulePermissionAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

    def response_post_save_add(self, request, obj):
        opts = MyUser._meta

        if self.has_change_permission(request, None):
            post_url = reverse('admin:%s_%s_changelist' %
                               (opts.app_label, opts.model_name),
                               current_app=self.admin_site.name)
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def response_post_save_change(self, request, obj):
        opts = MyUser._meta

        if self.has_change_permission(request, None):
            post_url = reverse('admin:%s_%s_changelist' %
                               (opts.app_label, opts.model_name),
                               current_app=self.admin_site.name)
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(MyUser, UserAdmin)
admin.site.register(Student, NoModulePermissionAdmin)
admin.site.register(Lecturer, NoModulePermissionAdmin)
