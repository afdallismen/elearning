import nested_admin

from django.forms import ValidationError


class BaseQuestionFormSet(nested_admin.NestedInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        if self.forms and any([form.cleaned_data for form in self.forms]):
            total = 0
            for form in self.forms:
                if form.cleaned_data:
                    total += form.cleaned_data['score_percentage']

            if total < 100:
                empty_score = []
                for form in self.forms:
                    if form.cleaned_data['score_percentage'] == 0:
                        empty_score.append(form)

                if empty_score:
                    assigned_score = (100 - total) // len(empty_score)
                    for form in self.forms:
                        if form in empty_score:
                            inst = form.save(commit=False)
                            inst.assignment = self.instance.save()
                            inst.score_percentage = assigned_score
                            inst.save()
                else:
                    raise ValidationError("Make sure score percentage "
                                          "add up to 100.")
            elif total > 100:
                raise ValidationError("Make sure score percentage "
                                      "add up to 100.")
