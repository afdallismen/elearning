from django.utils import timezone


def user_avatar_directory_path(instance, filename):
    now = timezone.now()
    return 'account/{0}/{1}'.format(
        "".join((str(now.year), str(now.month), str(now.day))), filename)
