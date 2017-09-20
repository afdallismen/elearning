from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def letter(value):
    value = int(value)
    if 85 <= value <= 100:
        return "A"
    elif 75 <= value <= 84:
        return "B"
    elif 60 <= value <= 74:
        return "C"
    elif 50 <= value <= 59:
        return "D"
    else:
        return "E"
