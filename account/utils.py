def user_directory_path(instance, filename):
    return 'account/{0}/{1}'.format(instance.user.id, filename)
