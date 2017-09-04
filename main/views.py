from django.shortcuts import render, redirect
from django.urls import reverse


def auth_index(request):
    return render(request, 'main/auth_index.html')


def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(reverse('admin:index'))
        else:
            return auth_index(request)
    return render(request, 'main/index.html')
