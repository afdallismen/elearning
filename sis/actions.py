from django.shortcuts import render
from django.utils.translation import ugettext as _

from account.models import Student
from sis.models import Assignment


def print_students_result(model_admin, request, queryset):
    students = Student.objects.filter(pk__in=queryset.values_list('student'))
    exercises = Assignment.objects.filter(category=0)
    quizes = Assignment.objects.filter(category=1)
    mids = Assignment.objects.filter(category=2)
    finals = Assignment.objects.filter(category=3)
    data = dict()
    for student in students:
        data[student.user.name.title()] = dict()
        data[student.user.name.title()]['nobp'] = student.nobp
        data[student.user.name.title()]['belong_in'] = student.belong_in.name
        data[student.user.name.title()]['result'] = student.finalresult.score
        data[student.user.name.title()]['exercise'] = []
        data[student.user.name.title()]['quiz'] = []
        data[student.user.name.title()]['mid'] = []
        data[student.user.name.title()]['final'] = []
        for exercise in exercises:
            if student.assignmentresult_set.filter(assignment__pk=exercise.pk):
                data[student.user.name.title()]['exercise'].append((
                    exercise.pk,
                    student.assignmentresult_set.get(
                        assignment__pk=exercise.pk
                    ).score
                ))
            else:
                data[student.user.name.title()]['exercise'].append((
                    exercise.pk,
                    "-"
                ))
        for quiz in quizes:
            if student.assignmentresult_set.filter(assignment__pk=quiz.pk):
                data[student.user.name.title()]['quiz'].append((
                    quiz.pk,
                    student.assignmentresult_set.get(
                        assignment__pk=quiz.pk
                    ).score
                ))
            else:
                data[student.user.name.title()]['quiz'].append((quiz.pk, "-"))
        for mid in mids:
            if student.assignmentresult_set.filter(assignment__pk=mid.pk):
                data[student.user.name.title()]['mid'].append((
                    mid.pk,
                    student.assignmentresult_set.get(
                        assignment__pk=mid.pk
                    ).score
                ))
            else:
                data[student.user.name.title()]['mid'].append((mid.pk, "-"))
        for final in finals:
            if student.assignmentresult_set.filter(assignment__pk=final.pk):
                data[student.user.name.title()]['final'].append((
                    final.pk,
                    student.assignmentresult_set.get(
                        assignment__pk=final.pk
                    ).score
                ))
            else:
                data[student.user.name.title()]['final'].append((
                    final.pk,
                    "-"
                ))
    contexts = {
        'data': data,
        'assignments': {
            'exercises': exercises,
            'quizes': quizes,
            'mids': mids,
            'finals': finals,
        }
    }
    return render(
        request,
        'print/students_result.html',
        contexts
    )
print_students_result.short_description = _("Print selected users score") # noqa
