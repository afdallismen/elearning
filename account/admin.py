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
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2'), }),
    )
    list_display = ('__str__', 'email', 'user_identity', 'is_active')
    list_filter = ('is_active', filter_group)

    def user_identity(self, obj):
        if not obj.is_student and not obj.is_lecturer:
            return self.empty_value_display

        classname, idt = obj.identity

        link = reverse("admin:account_{}_change".format(classname),
                       args=(getattr(obj, classname).pk, ))

        return format_html("<a href={}><b>{}</b></a>", link, idt)
    user_identity.short_description = _("identity number")


class NoModulePermissionAdmin(admin.ModelAdmin):
    readonly_fields = ['avatar_thumbnail']

    def has_module_permission(self, request):
        return False

    def response_post_save_add(self, request, obj):
        # Redirect user to MyUser changelist
        if self.has_change_permission(request, None):
            post_url = reverse(
                'admin:{!s}_{!s}_changelist'.format(
                    MyUser._meta.app_label, MyUser._meta.model_name
                ), current_app=self.admin_site.name
            )
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def response_post_save_change(self, request, obj):
        # Redirect user to MyUser changelist
        if self.has_change_permission(request, None):
            post_url = reverse(
                'admin:{!s}_{!s}_changelist'.format(
                    MyUser._meta.app_label, MyUser._meta.model_name
                ), current_app=self.admin_site.name
            )
        else:
            post_url = reverse('admin:index',
                               current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def avatar_thumbnail(self, obj):
        if hasattr(obj, 'avatar_thumbnail') and obj.avatar:
            url = obj.avatar_thumbnail.url
        else:
            url = "{% static 'img/stock_avatar.jpg' %}"

        return format_html('<img src={} />', url)
    avatar_thumbnail.short_description = ""


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Student, NoModulePermissionAdmin)
admin.site.register(Lecturer, NoModulePermissionAdmin)
