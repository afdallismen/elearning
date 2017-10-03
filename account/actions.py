from django.utils.translation import ugettext as _


def activate_users(model_admin, request, queryset):
    for user in queryset:
        if user.is_student or user.is_lecturer:
            queryset.update(is_active=True)
activate_users.short_description = _("Make selected users account active") # noqa


def deactivate_users(model_admin, request, queryset):
    queryset.update(is_active=False)
deactivate_users.short_description = _("Make selected users account inactive") # noqa
