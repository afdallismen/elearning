MAHASISWA_CHANGE_LINK = "".join((
    '<a href="{}" style="margin-right:10px">',
    '<i class="fa fa-vcard-o" aria-hidden="true"></i> Student',
    '</a>'))
DOSEN_CHANGE_LINK = "".join((
    '<a href="{}" style="margin-right:10px">'
    '<i class="fa fa-vcard-o" aria-hidden="true"></i> Lecturer'
    '</a>'))
PENGGUNA_CHANGE_LINK = "".join((
    '<a href="{}" style="margin-right:10px">'
    '<i class="fa fa-user-circle-o" aria-hidden="true"></i> User'
    '</a>'))
DELETE_LINK = "".join((
    '<a href="{}">',
    '<i class="fa fa-times" aria-hidden="true"></i> Delete'
    '</a>'))


def user_avatar_directory_path(instance, filename):
    return 'account/{0}/{1}'.format(instance.user.id, filename)
