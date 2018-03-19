from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Student
from sis.models import Assignment, AssignmentResult, FinalResult


@receiver(post_save, sender=Student)
def create_final_report(sender, instance, created, **kwargs):
    if created:
        FinalResult.objects.get_or_create(student=instance)


@receiver(post_save, sender=Student)
def create_assignment_report(sender, instance, created, **kwargs):
    if created:
        assignments = Assignment.objects.filter(
            courses=instance.belong_in,
            status=1
        )
        for assignment in assignments:
            AssignmentResult.objects.create(
                student=instance,
                assignment=assignment
            )
