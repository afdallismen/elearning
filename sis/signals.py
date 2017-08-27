from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from sis.models import Answer, AssignmentResult, FinalResult


@receiver(post_save, sender=Answer)
def create_report(sender, instance, created, **kwargs):
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
    report.score = sum(total_score) / len(total_score)
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
