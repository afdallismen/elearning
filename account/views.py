from django.forms.models import modelform_factory
from django.shortcuts import render

from account.models import MyUser, Student
from sis.models import Assignment
from sis.decorators import redirect_admin


@redirect_admin
def edit(request):
    BaseUserForm = modelform_factory(
        MyUser,
        fields=['username', 'first_name', 'last_name', 'email']
    )
    BaseStudentForm = modelform_factory(
        Student,
        fields=['nobp', 'belong_in', 'avatar']
    )
    userform = BaseUserForm(instance=request.user, prefix="usr")
    studentform = BaseStudentForm(instance=request.user.student, prefix="std")
    if request.method == "POST":
        userform = BaseUserForm(
            request.POST,
            instance=request.user,
            prefix="usr"
        )
        studentform = BaseStudentForm(
            request.POST,
            request.FILES,
            instance=request.user.student,
            prefix="std"
        )
        if userform.is_valid() and studentform.is_valid():
            userform.save()
            studentform.save()
    contexts = {
        'userform': userform,
        'studentform': studentform
    }
    return render(request, 'account/edit.html', contexts)


def print_result(request):
    assignments = Assignment.objects.all()
    data = dict()
    for assignment in assignments:
        data[str(assignment).title()] = []
        total = 0
        for question in assignment.question_set.all():
            answers = request.user.student.answer_set
            if answers.filter(question=question).exists():
                total = int(total) + (question.score_percentage * answers.get(question=question).score) // 100 # noqa
                data[str(assignment).title()].append(
                    (
                        str(question),
                        question.score_percentage,
                        answers.get(question=question).score,
                        (question.score_percentage * answers.get(question=question).score) // 100 # noqa
                    )
                )
            else:
                data[str(assignment).title()].append(
                    (
                        str(question),
                        question.score_percentage,
                        0,
                        0
                    )
                )
        data[str(assignment).title()].append(total if total else int(0))
    return render(request, 'print/student_result.html', {'data': data})
