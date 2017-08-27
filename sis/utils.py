from django.utils.html import strip_tags


def attachment_directory(instance, filename):
    return "attachment/{}/{}/{}".format(
        str(instance.content_type.name),
        str(instance.object_id),
        filename
    )


def nstrip_tags(n, text):
    text = strip_tags(text)
    if len(text) > n:
        return text[:n] + "..."
    return text
