from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from sis.models import Answer, AssignmentResult, FinalResult, Assignment


@receiver(post_save, sender=Answer)
def create_result(sender, instance, created, **kwargs):
    report = {
        'student': instance.student,
        'assignment': instance.question.assignment
    }
    report, _ = AssignmentResult.objects.get_or_create(**report)
    report.score = get_assignment_score(instance)
    report.save()

    report, _ = FinalResult.objects.get_or_create(student=instance.student)
    total_score = []
    for rep in AssignmentResult.objects.filter(student=instance.student):
        total_score.append(rep.score)
    report.score = sum(total_score) / Assignment.objects.count()
    report.save()


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

    report, _ = FinalResult.objects.get_or_create(student=instance.student)
    total_score = []
    for rep in AssignmentResult.objects.filter(student=instance.student):
        total_score.append(rep.score)
    report.score = sum(total_score) / Assignment.objects.count()
    report.save()


def get_assignment_score(answer):
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
