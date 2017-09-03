from django.contrib.auth.models import User

from registration.forms import RegistrationFormUniqueEmail as RegistrationForm

from account.models import Student


class StudentRegistrationForm(RegistrationForm):
    nobp = Student._meta.get_field('nobp').formfield()

    class Meta(RegistrationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            'email',
            'password1',
            'password2',
            'nobp',
        ]
        required_css_class = 'required'

    def save(self, commit=True):
        user = super(StudentRegistrationForm, self).save(commit)
        if commit:
            Student.get_or_create(
                user=user,
                nobp=self.cleaned_data['nopb'])
        return user
