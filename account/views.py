from django.shortcuts import render


def detail(request):
    return render(request, 'account/detail.html')
