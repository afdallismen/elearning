from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _

from account.models import Student


class StudentInline(admin.StackedInline):
    can_delete = False
    model = Student
    template = 'admin/edit_inline/stacked.html'
    verbose_name_plural = 'extra info'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (StudentInline, )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
