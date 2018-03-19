from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from sis.models import Assignment, Question


def redirect_admin(fn):
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.user.is_staff:
            return redirect(reverse('admin:index'))
        else:
            return fn(*args, **kwargs)
    return wrapper


def reject_draft(fn):
    def wrapper(*args, **kwargs):
        pk = kwargs['pk']
        assignment = Assignment.objects.get(pk=pk)
        if assignment.status == 0:
            raise Http404('Assignment not avaible')
        else:
            return fn(*args, **kwargs)
    return wrapper


def reject_expired(fn):
    def wrapper(*args, **kwargs):
        pk = kwargs['pk']
        assignment = Question.objects.get(pk=pk).assignment
        if assignment.has_expired and not args[0].method == 'POST':
            raise Http404('Assignment has expired')
        else:
            return fn(*args, **kwargs)
    return wrapper
