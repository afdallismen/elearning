from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from account.models import Student
from sis.models import (
    Answer, AssignmentResult, Assignment, FinalResultPercentage)


@receiver(post_save, sender=Answer)
def create_result(sender, instance, created, **kwargs):
    report = {'student': instance.student,
              'assignment': instance.question.assignment}
    result, _ = AssignmentResult.objects.get_or_create(**report)
    result.score = _get_assignment_result(instance)
    result.save()

    _update_final_result(instance.student)


@receiver(post_delete, sender=Answer)
def delete_result(sender, instance, using, **kwargs):
    assignment = instance.question.assignment
    student = instance.student
    exist = Answer.objects.filter(
        student=student, question__assignment=assignment).exists()
    if not exist:
        AssignmentResult.objects.filter(
            student=student, assignment=assignment
        ).delete()

    _update_final_result(instance.student)


@receiver(post_save, sender=FinalResultPercentage)
@receiver([post_save, post_delete], sender=Assignment)
def update_final_result(sender, instance, *args, **kwargs):
    students = Student.objects.all()
    for student in students:
        _update_final_result(student)


def _update_final_result(student):
    qs = AssignmentResult.objects.filter(student=student)
    results = {'quiz': qs.filter(assignment__category=0),
               'mid': qs.filter(assignment__category=1),
               'final': qs.filter(assignment__category=2)}
    score = {'quiz': sum(ar.score for ar in results['quiz']),
             'mid': sum(ar.score for ar in results['mid']),
             'final': sum(ar.score for ar in results['final'])}
    percentage = FinalResultPercentage.objects.get()
    total_score = 0
    for key, value in score.items():
        total_score += (value * getattr(percentage, key)) / 100
    student.finalresult.score = total_score
    student.finalresult.save()


def _get_assignment_result(answer):
    assignment = answer.question.assignment
    questions = assignment.question_set.all()
    answers = []

    for question in questions:
        try:
            answers.append(
                Answer.objects.get(
                    question=question.pk, student=answer.student.pk
                )
            )
        except ObjectDoesNotExist:
            pass

    final_score = 0
    for answer in answers:
        final_score += (answer.score * answer.question.score_percentage) / 100
    return final_score
