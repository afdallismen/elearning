from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Student, Lecturer
from sis.models import FinalResult


@receiver(post_save, sender=Student)
def create_final_report(sender, instance, created, **kwargs):
    if created:
        FinalResult.objects.get_or_create(student=instance)


@receiver(post_save, sender=Student)
def assign_student(sender, instance, created, **kwargs):
    if created:
        group, ign = Group.objects.get_or_create(name="student")
        instance.user.groups.add(group)
        instance.user.save()


@receiver(post_save, sender=Lecturer)
def assign_lecturer(sender, instance, created, **kwargs):
    if created:
        group, ign = Group.objects.get_or_create(name="lecturer")
        instance.user.groups.add(group)
        instance.user.save()
