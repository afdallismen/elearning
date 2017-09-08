from django.utils import timezone


def user_avatar_directory_path(instance, filename):
    now = timezone.now()
    return 'account/{dt:%Y%m%d}/{filename}'.format(dt=now, filename=filename)
