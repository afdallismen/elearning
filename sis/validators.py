from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _


class MinDateValueValidator(MinValueValidator):
    message = _('Ensure this value is greater'
                ' than or equal to today\'s date.')
    code = 'min_value'

    def compare(self, a, b):
        return a < b
