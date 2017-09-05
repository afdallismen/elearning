from django.db.models import Count
from django.shortcuts import render

from sis.models import Module, Assignment, Answer, Question, AssignmentResult


def module_index(request):
    modules = Module.objects.all()
    if request.GET.get('q', ''):
        modules = modules.filter(title__icontains=request.GET['q'])

    return render(
        request,
        'sis/module/index.html',
        {'modules': modules, 'active': 'module'})


def module_detail(request, slug):
    module = Module.objects.get(slug=slug)

    return render(
        request,
        'sis/module/detail.html',
        {'module': module, 'active': 'module'}
    )


def assignment_index(request):
    assignments = Assignment.objects.all()

    finish_get = request.GET.get('finish', None)
    if finish_get is not None:
        student_assignment = AssignmentResult.objects.filter(
            student=request.user.student).values_list('assignment', flat=True)
        assignments = []
        for assignment in Assignment.objects.filter(id__in=student_assignment):
            finished = True
            for question in assignment.question_set.all():
                if not Answer.objects.filter(
                        student=request.user.student,
                        question=question).exists():
                    finished = False
            if finished:
                assignments.append(assignment)
        if finish_get == "False":
            assignments = set(Assignment.objects.all()) - set(assignments)

    return render(
        request,
        'sis/assignment/index.html',
        {'assignments': assignments, 'active': 'assignment'})


def assignment_detail(request, pk):
    if request.method == "POST":
        text = request.POST['text']
        question = request.POST['question']
        print(question)
        if text:
            obj, ign = Answer.objects.get_or_create(
                student=request.user.student,
                question=Question.objects.get(id=question))
            obj.text = text
            obj.save()
    assignment = Assignment.objects.get(pk=pk)
    user_questions = Answer.objects.filter(
        student=request.user.student).values_list(
        'question', flat=True).annotate(
        Count('question'))
    user_answers = dict()
    for question in user_questions:
        user_answer = Answer.objects.get(
            student=request.user.student, question=question)
        user_answers['question'] = user_answer

    return render(
        request,
        'sis/assignment/detail.html',
        {
            'assignment': assignment,
            'user_questions': user_questions,
            'user_answers': user_answers,
            'active': 'assignment'
        }
    )
