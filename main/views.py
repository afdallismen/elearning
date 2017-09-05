from django.shortcuts import render, redirect
from django.urls import reverse

from sis.views import module_index


def auth_index(request):
    return module_index(request)


def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(reverse('admin:index'))
        else:
            return auth_index(request)
    return render(request, 'main/index.html')
