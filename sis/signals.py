from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from account.models import Student
from sis.models import Answer, AssignmentResult, Assignment


@receiver(post_save, sender=Answer)
def create_result(sender, instance, created, **kwargs):
    report = {
        'student': instance.student,
        'assignment': instance.question.assignment
    }
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


@receiver([post_save, post_delete], sender=Assignment)
def update_final_result(sender, instance, *args, **kwargs):
    students = Student.objects.all()
    for student in students:
        _update_final_result(student)


def _update_final_result(student):
    total_score = sum(
        AssignmentResult.objects.filter(student=student).values_list(
            'score', flat=True))
    student.finalresult.score = total_score / Assignment.objects.count()
    student.finalresult.save()


def _get_assignment_result(answer):
    assignment = answer.question.assignment
    questions = assignment.question_set.all()
    answers = []

    for question in questions:
        try:
            answers.append(
                Answer.objects.get(
                    question=question.pk, student=answer.student.pk))
        except ObjectDoesNotExist:
            pass

    final_score = 0
    for answer in answers:
        final_score += (answer.score * answer.question.score_percentage) / 100
    return final_score
