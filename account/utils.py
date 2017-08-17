def user_avatar_directory_path(instance, filename):
    return 'account/{0}/{1}'.format(instance.user.id, filename)


def validate_nobp(value):
    pass
