from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Student, Lecturer


@receiver(post_save, sender=User)
def in_active_user(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        instance.is_active = False
        instance.save()


@receiver(post_save, sender=User)
def create_student_or_lecturer(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        instance.groups.add(Group.objects.get(name='student'))
        instance.save()
        Student.objects.get_or_create(user=instance)
    elif created and instance.is_superuser:
        instance.groups.add(Group.objects.get(name='lecturer'))
        instance.save()
        Lecturer.objects.get_or_create(user=instance)
