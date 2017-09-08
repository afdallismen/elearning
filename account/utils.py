from django.utils import timezone


def user_avatar_directory_path(instance, filename):
    now = timezone.now()
    return 'account/{0:%Y%m%d}/{1}'.format(now, filename)
