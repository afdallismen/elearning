from django.core.urlresolvers import reverse
from django.utils.html import format_html


def object_link(url, text, pk):
    return format_html(
        '<a href="{}">{}</a>',
        reverse(url, args=(pk, )),
        text
    )


def object_icon_link(url, icon, text, pk):
    return format_html(
        '<a href="{}" style="margin-right:10px">{} {}</a>',
        reverse(url, args=(pk, )),
        icon,
        text
    )
