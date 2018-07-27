import nested_admin
from djangoformsetjs.utils import formset_media_js

from django import forms
from django.utils.translation import ugettext as _

from sis.models import Attachment


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
                    count = 1
                    for form in self.forms:
                        if form in empty_score:
                            question = form.save(commit=False)
                            question.score_percentage = assigned_score
                            if self.instance._state.adding:
                                self.instance.save()
                            question.save()
                        count = count + 1
                else:
                    raise forms.ValidationError(_("Make sure score percentage "
                                          "add up to 100."))
            elif total > 100:
                raise forms.ValidationError(_("Make sure score percentage "
                                      "add up to 100."))


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file_upload']
    class Media:
        js = formset_media_js


FileUploadFormset = forms.models.modelformset_factory(
    Attachment,
    form=AttachmentForm,
    fields=['file_upload'],
    widgets={'file_upload': forms.ClearableFileInput(attrs={
            'class': "form-control-file",
            'label': "Lampiran"
        })
    }
)
