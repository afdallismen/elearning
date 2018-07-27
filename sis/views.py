from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from sis.decorators import redirect_admin, reject_draft, reject_expired
from sis.forms import FileUploadFormset
from sis.models import Module, Assignment, Question, Answer, Attachment


@login_required
@redirect_admin
def module_detail(request, slug):
    try:
        module = Module.objects.get(slug=slug)
    except Module.DoesNotExist:
        raise Http404("Module does not exist")
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
        raise Http404("Assignment does not exist")
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
        answer, created = Answer.objects.get_or_create(
            student=request.user.student,
            question=question,
        )
        content_type = ContentType.objects.get_for_model(
            Answer)
        attachments = Attachment.objects.filter(
            content_type=content_type,
            object_id=answer.id,
        ).values('file_upload')
        formset = FileUploadFormset(queryset=attachments)
        initials = attachments.values('file_upload')
        if initials.exists():
            formset = FileUploadFormset(initial=initials)
        if request.method == "POST":
            text = request.POST.get('text', None)
            answer.text = text
            answer.save()
            data = FileUploadFormset(request.POST, request.FILES)
            if data.is_valid():
                instances = data.save(commit=False)
                for instance in instances:
                    instance.content_type = content_type
                    instance.object_id = answer.id
                    instance.save()
            return redirect(
                reverse(
                    'sis:assignment_detail',
                    kwargs={'pk': question.assignment_id}
                )
            )
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    contexts = {
        'answer': answer,
        'question': question,
        'formset': formset
    }
    return render(request, 'sis/form_answer.html', contexts)
