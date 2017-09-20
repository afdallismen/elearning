from django.shortcuts import redirect
from django.urls import reverse


def redirect_admin(fn):
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.user.is_staff:
            return redirect(reverse('admin:index'))
        else:
            return fn(*args, **kwargs)
    return wrapper
