import nested_admin

from django.forms import ValidationError
from django.utils.translation import ugettext as _

class BaseQuestionFormSet(nested_admin.NestedInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        if self.forms and any([form.cleaned_data for form in self.forms]):
            total = sum(form.cleaned_data['score_percentage']
                        for form in self.forms if form.cleaned_data)

            if total < 100:
                empty_score = [form for form in self.forms
                               if form.cleaned_data['score_percentage'] == 0]

                if empty_score:
                    assigned_score = (100 - total) // len(empty_score)
                    for form in self.forms:
                        if form in empty_score:
                            obj = form.save(commit=False)
                            obj.assignment = self.instance.save()
                            obj.score_percentage = assigned_score
                            obj.save()
                else:
                    raise ValidationError(_("Make sure score percentage "
                                          "add up to 100."))
            elif total > 100:
                raise ValidationError(_("Make sure score percentage "
                                      "add up to 100."))
