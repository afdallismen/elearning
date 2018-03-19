from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def letter(value):
    value = int(value)
    if 87 <= value <= 100:
        return "A"
    elif 81 <= value <= 86:
        return "A-"
    elif 74 <= value <= 80:
        return "B+"
    elif 68 <= value <= 73:
        return "B"
    elif 62 <= value <= 67:
        return "C+"
    elif 50 <= value <= 61:
        return "C"
    elif 43 <= value <= 49:
        return "C-"
    elif 25 <= value <= 42:
        return "D"
    else:
        return "E"
