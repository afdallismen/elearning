from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from account.models import MyUser


def dashboard(request):
    request.user = MyUser.objects.get(pk=request.user.pk)
    return render(request, 'main/dashboard.html')


@login_required
def index(request):
    if request.user.is_staff:
        return redirect(reverse('admin:index'))
    else:
        return dashboard(request)
