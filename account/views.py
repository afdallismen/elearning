from django.forms.models import modelform_factory
from django.shortcuts import render

from account.models import MyUser, Student
from sis.decorators import redirect_admin


@redirect_admin
def edit(request):
    BaseUserForm = modelform_factory(
        MyUser,
        fields=['username', 'first_name', 'last_name', 'email']
    )
    BaseStudentForm = modelform_factory(
        Student,
        fields=['nobp', 'avatar']
    )
    userform = BaseUserForm(instance=request.user, prefix='usr')
    studentform = BaseStudentForm(instance=request.user.student, prefix='std')
    if request.method == "POST":
        userform = BaseUserForm(
            request.POST,
            instance=request.user,
            prefix='usr'
        )
        studentform = BaseStudentForm(
            request.POST,
            request.FILES,
            instance=request.user.student,
            prefix='std'
        )
        if userform.is_valid() and studentform.is_valid():
            userform.save()
            studentform.save()
    contexts = {
        'userform': userform,
        'studentform': studentform
    }
    return render(request, 'account/edit.html', contexts)
