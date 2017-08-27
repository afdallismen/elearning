from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from sis.models import Answer, Report


@receiver(post_save, sender=Answer)
def create_report(sender, instance, created, **kwargs):
    report = {
        'student': instance.student,
        'assignments': instance.question.assignment
    }
    report, _ = Report.objects.get_or_create(**report)
    report.final_score = get_final_score(instance)
    report.save()


def get_final_score(answer):
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
