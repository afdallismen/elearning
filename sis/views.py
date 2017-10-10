from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from sis.decorators import redirect_admin, reject_draft, reject_expired
from sis.models import Module, Assignment, Question, Answer


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
@reject_draft
def assignment_detail(request, pk):
    try:
        assignment = Assignment.objects.get(pk=pk)
        answered = request.user.student.answer_set.filter(
            question__in=assignment.question_set.all()
        ).values_list('question', flat=True)
    except Assignment.DoesNotExist:
        raise Http404('Assignment does not exist')
    return render(
        request,
        'sis/assignment_detail.html',
        {
            'assignment': assignment,
            'answered': answered
        }
    )


@login_required
@redirect_admin
@reject_expired
def do_answer(request, pk):
    try:
        question = Question.objects.get(pk=pk)
        try:
            answer = request.user.student.answer_set.get(question=question)
            if request.method == "POST":
                text = request.POST.get('text', None)
                if answer:
                    answer.text = text
                    answer.save()
                return redirect(
                    reverse(
                        'sis:assignment_detail',
                        kwargs={'pk': question.assignment_id}
                    )
                )
        except Answer.DoesNotExist:
            answer = False
            if request.method == "POST":
                answer = request.POST.get('text', None)
                if answer:
                    Answer.objects.get_or_create(
                        student=request.user.student,
                        question=question,
                        text=answer
                    )
                return redirect(
                    reverse(
                        'sis:assignment_detail',
                        kwargs={'pk': question.assignment_id}
                    )
                )
    except Question.DoesNotExist:
        raise Http404('Question does not exist')
    contexts = {
        'answer': answer,
        'question': question
    }
    return render(request, 'sis/form_answer.html', contexts)
