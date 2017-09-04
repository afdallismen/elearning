import base64

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.html import strip_tags, format_html
from django.utils.translation import ugettext as _


from imagekit import ImageSpec
from imagekit.processors import ResizeToFill


class Thumbnail(ImageSpec):
    processors = [ResizeToFill(640, 480)]
    format = 'JPEG'
    options = {'quality': 60}


def answer_admin_object_action_link(obj):
    return format_html(
        '<a href="{}" style="margin-right:10px">'
        '<i class="fa fa-file-text-o" aria-hidden="true"></i> Answer'
        '</a>',
        reverse("admin:sis_answer_change", args=(obj.id, )))


def attachment_directory(instance, filename):
    now = timezone.now()
    return "attachment/{0}/{1}/{2}".format(
        instance.content_type.name,
        "".join((str(now.year), str(now.month), str(now.day))),
        filename)


def nstrip_tags(n, text):
    text = strip_tags(text)
    if len(text) > n:
        return text[:n] + "..."
    return text


def file_html_display(field_file, width, height):
    file_type = field_file.name.split(".")[-1].lower()
    if file_type == "swf":
        return _get_swf_html_display(field_file.url, width, height)
    elif file_type in ['mp4', 'webm']:
        return _get_video_html_display(field_file.url, width, height)
    elif file_type in ['jpeg', 'jpg', 'png']:
        thumb = Thumbnail(source=field_file.file).generate()
        img_bytes = base64.b64encode(thumb.getvalue())
        return _get_image_html_display(img_bytes)
    elif file_type in ['doc', 'xsl', 'docx', 'xlsx', 'pdf', 'ppt', 'pptx']:
        return _get_docs_html_display(field_file.url)
    else:
        return _("No preview available for this file type.")


def _get_swf_html_display(url, width, height):
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

    return format_html(
        html_tag, src=url, width=width, height=height)


def _get_video_html_display(url, width, height):
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


def _get_image_html_display(img_bytes):
    html_tag = '<img src="data:image/jpeg;base64,{}"/>'

    return format_html(html_tag, img_bytes)


def _get_docs_html_display(url):
    html_tag = '''
        <a target='_blank'
            href='https://view.officeapps.live.com/op/embed.aspx?src={}'
            >View on new window
        </a>'''
    url = "http://localhost:8000{}".format(url)
    return format_html(html_tag, url)
