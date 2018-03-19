from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from account.actions import activate_users, deactivate_users
from account.filters import (
    UserIdentityListFilter as filter_identity,
    StudentSemesterListFilter as filter_semester
)
from account.models import Student, Lecturer, MyUser
from main.utils import object_link


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
    list_display = ('name_display', 'identity_display', 'semester_display',
                    'class_display', 'is_active')
    list_display_links = None
    list_filter = ('is_active', filter_identity, 'student__belong_in',
                   filter_semester)

    def name_display(self, obj):
        return object_link(
            'admin:account_myuser_change',
            obj.name.title(),
            obj.pk
        )
    name_display.short_description = _("name")
    name_display.admin_order_field = 'username'

    def identity_display(self, obj):
        return object_link(
            'admin:account_{}_change'.format(obj.identity[0]),
            obj.identity[1],
            getattr(obj, obj.identity[0]).pk
        )
    identity_display.short_description = _("identity number")
    identity_display.admin_order_field = 'student__nobp'

    def semester_display(self, obj):
        if obj.is_student:
            return obj.student.semester
        return self.empty_value_display
    semester_display.short_description = _("semester")
    semester_display.admin_order_field = 'student__nobp'

    def class_display(self, obj):
        if obj.is_student:
            return obj.student.belong_in
        return self.empty_value_display
    class_display.short_description = _("class")
    class_display.admin_order_field = 'student__belong_in'


class NoModulePermissionAdmin(admin.ModelAdmin):
    readonly_fields = ['avatar_thumbnail']

    def has_module_permission(self, request):
        return False

    def response_post_save_add(self, request, obj):
        # Redirect user to MyUser changelist
        if self.has_change_permission(request, None):
            post_url = reverse(
                'admin:{!s}_{!s}_changelist'.format(
                    MyUser._meta.app_label,
                    MyUser._meta.model_name
                ),
                current_app=self.admin_site.name
            )
        else:
            post_url = reverse(
                'admin:index',
                current_app=self.admin_site.name
            )
        return HttpResponseRedirect(post_url)

    def response_post_save_change(self, request, obj):
        # Redirect user to MyUser changelist
        if self.has_change_permission(request, None):
            post_url = reverse(
                'admin:{!s}_{!s}_changelist'.format(
                    MyUser._meta.app_label,
                    MyUser._meta.model_name
                ),
                current_app=self.admin_site.name
            )
        else:
            post_url = reverse(
                'admin:index',
                current_app=self.admin_site.name
            )
        return HttpResponseRedirect(post_url)

    def avatar_thumbnail(self, obj):
        if hasattr(obj, 'avatar_thumbnail') and obj.avatar:
            url = obj.avatar_thumbnail.url
        else:
            url = "/static/img/stock_avatar.jpg"

        return format_html('<img src={} />', url)
    avatar_thumbnail.short_description = _("profile picture")


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Student, NoModulePermissionAdmin)
admin.site.register(Lecturer, NoModulePermissionAdmin)
