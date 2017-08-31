from django.core.urlresolvers import reverse
from django.utils.html import strip_tags, format_html


def answer_admin_object_action_link(obj):
    return format_html(
        '<a href="{}" style="margin-right:10px">'
        '<i class="fa fa-file-text-o" aria-hidden="true"></i> Answer'
        '</a>',
        reverse("admin:sis_answer_change", args=(obj.id, )))


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
