from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Student, MyUser
from sis.models import FinalResult


@receiver(post_save, sender=MyUser)
def assign_groups(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            group, ign = Group.objects.get_or_create(name="lecturer")
        else:
            group, ign = Group.objects.get_or_create(name="student")
        instance.groups.add(group)
        instance.save()


@receiver(post_save, sender=Student)
def create_final_report(sender, instance, created, **kwargs):
    if created:
        FinalResult.objects.get_or_create(student=instance)


@receiver(post_save, sender=Student)
def update_course(sender, instance, created, **kwargs):
    course = instance.belong_in
    if course:
        student_count = course.student_set.count()
        if student_count >= course.capacity:
            course.is_filled = True
        else:
            course.is_filled = False
        course.save()
