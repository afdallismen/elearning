from django.utils import timezone


def user_avatar_directory_path(instance, filename):
    now = timezone.now()
    return 'account/{0}/{1}'.format(
        "".join((now.year, now.month, now.day)), filename)
