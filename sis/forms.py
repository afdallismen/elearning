import nested_admin

from django.forms import ValidationError
from django.utils.translation import ugettext as _


class BaseQuestionFormSet(nested_admin.NestedInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        total = sum((
            form.cleaned_data['score_percentage'] for form in self.forms))
        if 0 < total < 100 or total > 100:
            raise ValidationError(_("Make sure question score percentage "
                                    "add up to 100."))
