from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from registration.forms import RegistrationFormUniqueEmail as RegistrationForm

from account.models import MyUser, Student


class StudentRegistrationForm(RegistrationForm):
    nobp = Student._meta.get_field('nobp').formfield()

    class Meta(RegistrationForm.Meta):
        model = MyUser
        fields = [User.USERNAME_FIELD,
                  'email',
                  'password1',
                  'password2',
                  'nobp']
        required_css_class = 'required'

    def clean(self):
        super(StudentRegistrationForm, self).clean()

        # Manually validate nobp
        try:
            Student.NOBPVALIDATOR(self.cleaned_data['nobp'])
        except ValidationError as err:
            raise ValidationError({'nobp': err.message})

        # Check unique nobp
        if Student.objects.filter(nobp=self.cleaned_data['nobp']).exists():
            raise ValidationError(
                {'nobp': _("User with with no bp you entered has regitered.")}
            )

    def save(self, commit=True):
        user = super(StudentRegistrationForm, self).save(commit)
        user.save()
        Student.objects.get_or_create(user=user,
                                      nobp=self.cleaned_data['nobp'])
        return user


class StudentChangeForm(UserChangeForm):
    nobp = Student._meta.get_field('nobp').formfield()
    avatar = Student._meta.get_field('avatar').formfield()

    class Meta(RegistrationForm.Meta):
        model = MyUser
        fields = [User.USERNAME_FIELD,
                  'email',
                  'password',
                  'first_name',
                  'last_name',
                  'nobp',
                  'avatar']
        required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(StudentChangeForm, self).__init__(*args, **kwargs)
        self.initial['nobp'] = self.instance.student.nobp
        self.initial['avatar'] = self.instance.student.avatar

    def clean(self):
        super(StudentChangeForm, self).clean()

        # Manually validate nobp
        try:
            Student.NOBPVALIDATOR(self.cleaned_data['nobp'])
        except ValidationError as err:
            raise ValidationError({'nobp': err.message})

        # Check unique nobp if nobp changed_data
        exist = Student.objects.filter(nobp=self.cleaned_data['nobp']).exists()
        changed = self.fields['nobp'].has_changed(self.fields['nobp'].initial,
                                                  self.cleaned_data['nobp'])
        if changed and exist:
            raise ValidationError(
                {'nobp': _("User with with no bp you entered has regitered.")}
            )

    def save(self, commit=True):
        user = super(StudentRegistrationForm, self).save(commit)
        user.student.update(nobp=self.cleaned_data['nobp'],
                            avatar=self.cleaned_data['avatar'])
        user.save()
        return user
