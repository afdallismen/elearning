from django.utils import timezone


def user_avatar_directory_path(instance, filename):
    now = timezone.now()
    return 'account/{:%Y%m%d}/{}'.format(now, filename)
