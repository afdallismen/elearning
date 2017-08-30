from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Student
from sis.models import FinalResult


@receiver(post_save, sender=User)
def assign_groups(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            group, _ = Group.objects.get_or_create(name='lecturer')
        else:
            group, _ = Group.objects.get_or_create(name='student')

        instance.groups.add(group)
        instance.save()


@receiver(post_save, sender=Student)
def create_final_report(sender, instance, created, **kwargs):
    if created:
        FinalResult.objects.get_or_create(student=instance)
