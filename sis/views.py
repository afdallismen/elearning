from django.shortcuts import render

from sis.models import Module


def index(request):
    modules = Module.objects.all()

    return render(
        request,
        'sis/modules/index.html',
        {'modules': modules, 'active': 'module'})


def detail(request, slug):
    module = Module.objects.get(slug=slug)

    return render(
        request,
        'sis/modules/detail.html',
        {'module': module, 'active': 'module'}
    )
