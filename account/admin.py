from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from account.filters import GroupListFilter as filter_group
from account.models import Student, Lecturer, MyUser


def activate_users(model_admin, request, queryset):
    for user in queryset:
        if hasattr(user, 'student') or hasattr(user, 'lecturer'):
            queryset.update(is_active=True)
activate_users.short_description = _("Make selected users as active") # noqa


def deactivate_users(model_admin, request, queryset):
    queryset.update(is_active=False)
deactivate_users.short_description = _("Make selected users as inactive") # noqa


# Define a new User admin
class MyUserAdmin(BaseUserAdmin):
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
    list_filter = ('is_active', filter_group)

    def identity(self, obj):
        if not obj.is_student and not obj.is_lecturer:
            return self.empty_value_display
        if obj.is_student:
            link = reverse("admin:account_student_change",
                           args=(obj.student.id, ))
            num = obj.student.nobp
        elif obj.is_lecturer:
            link = reverse("admin:account_lecturer_change",
                           args=(obj.lecturer.id, ))
            num = obj.lecturer.nip
        return format_html("<a href={}><b>{}</b></a>", link, num)
    identity.short_description = _("identity number")


class NoModulePermissionAdmin(admin.ModelAdmin):
    readonly_fields = ['avatar_thumbnail']

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

    def avatar_thumbnail(self, obj):
        avt = False

        if hasattr(obj, 'avatar_thumbnail') and obj.avatar:
            avt = obj.avatar_thumbnail.url

        if not avt:
            avt = "http://localhost:8000/media/account/stock_avatar.jpg"

        return format_html(
            '<img src={} />',
            avt)
    avatar_thumbnail.short_description = ""


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Student, NoModulePermissionAdmin)
admin.site.register(Lecturer, NoModulePermissionAdmin)
