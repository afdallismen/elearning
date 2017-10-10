import base64
from urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.html import strip_tags, format_html
from django.utils.translation import ugettext as _

from imagekit import ImageSpec
from imagekit.processors import ResizeToFill


FILE_EXTENSION = {
    'image': ['jpg', 'png'],
    'animation': ['swf'],
    'video': ['mp4', 'webm'],
    'doc': ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf']
}


class Thumbnail(ImageSpec):
    processors = [ResizeToFill(640, 480)]
    format = 'JPEG'
    options = {'quality': 100}


def answer_admin_change_link(pk):
    return format_html(
        '<a href="{}" style="margin-right:10px">'
        '<i class="fa fa-edit" aria-hidden="true"></i> Edit'
        '</a>',
        reverse("admin:sis_answer_change", args=(pk, ))
    )


def attachment_directory(instance, filename):
    now = timezone.now()
    return "attachment/{}/{:%Y%m%d}/{}".format(instance.content_type.name,
                                               now,
                                               filename)


def nstrip_tags(n, text):
    text = strip_tags(text)
    if len(text) > n:
        return text[:n] + "..."
    return text


def file_html_display(attachment, width, height):
    url = attachment.file_upload.url
    if attachment.is_animation:
        return _get_swf_display(url, width, height)

    elif attachment.is_video:
        return _get_video_display(url, width, height)

    elif attachment.is_image:
        thumb = Thumbnail(source=attachment.file_upload.file).generate()
        img_bytes = base64.b64encode(thumb.getvalue())
        return _get_image_display(url, img_bytes)

    elif attachment.is_doc:
        return _get_docs_display(url)

    else:
        return _("No preview available for this file type.")


def _get_swf_display(url, width, height):
    html_tag = '''
        <object type="application/x-shockwave-flash" data="{src}"
            width="{width}" height="{height}"
            style="border:1px solid #DCDCDC;">

            <param name="movie" value="{src}" />
            <param name="play" value="true" />
            <param name="allowfullscreen" value="true" />
            <param name="allowscriptaccess" value="always" />
            <param name="wmode" value="opaque" />
            <param name="quality" value="high" />
            <param name="menu" value="false" />
        </object>'''

    return format_html(html_tag, src=url, width=width, height=height)


def _get_video_display(url, width, height):
    html_tag = '''
        <video controls width="{width}" height="{height}"
            style="border:1px solid #DCDCDC;">
            <source src="{src}" type="video/webm">
            <source src="{src}" type="video/mp4">
            I'm sorry; your browser doesn't support HTML5 video in WebM
            with VP8/VP9 or MP4 with H.264.
        </video>'''

    return format_html(
        html_tag, src=url, width=width, height=height)


def _get_image_display(orig, img_bytes):
    html_tag = ('<a href="{orig}" target="_blank">'
                '<img src="data:image/jpeg;base64,{thumb}"></a>')

    return format_html(html_tag, orig=orig, thumb=img_bytes)


def _get_docs_display(url):
    html_tag = '''
        <a target='_blank'
            href='http://view.officeapps.live.com/op/view.aspx?src={}'
            >View on new window
        </a>'''
    encoded = urlencode(
        {'': "http://localhost:8000" + url}
    )[1:]
    return format_html(html_tag, encoded)
