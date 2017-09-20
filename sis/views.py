from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from sis.decorators import redirect_admin
from sis.models import Module, Assignment


@login_required
@redirect_admin
def module_detail(request, slug):
    try:
        module = Module.objects.get(slug=slug)
    except Module.DoesNotExist:
        raise Http404('Module does not exist')
    return render(request, 'sis/module_detail.html', {'module': module})


@login_required
@redirect_admin
def assignment_detail(request, pk):
    try:
        assignment = Assignment.objects.get(pk=pk)
    except Assignment.DoesNotExist:
        raise Http404('Assignment does not exist')
    return render(request, 'sis/assignment_detail.html', {
        'assignment': assignment})
