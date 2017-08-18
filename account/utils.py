MAHASISWA_CHANGE_LINK = "".join((
    '<a href="{}" style="margin-right:10px">',
    '<i class="fa fa-vcard-o" aria-hidden="true"></i> Mahasiswa',
    '</a>'))
DOSEN_CHANGE_LINK = "".join((
    '<a href="{}" style="margin-right:10px">'
    '<i class="fa fa-vcard-o" aria-hidden="true"></i> Dosen'
    '</a>'))
PENGGUNA_CHANGE_LINK = "".join((
    '<a href="{}" style="margin-right:10px">'
    '<i class="fa fa-user-circle-o" aria-hidden="true"></i> Pengguna'
    '</a>'))
DELETE_LINK = "".join((
    '<a href="{}">',
    '<i class="fa fa-times" aria-hidden="true"></i> Hapus'
    '</a>'))


def user_avatar_directory_path(instance, filename):
    return 'account/{0}/{1}'.format(instance.user.id, filename)


def validate_nobp(value):
    pass
