from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from registration.forms import RegistrationFormUniqueEmail as RegistrationForm

from account.models import MyUser, Student
from sis.models import Course


class StudentRegistrationForm(RegistrationForm):
    nobp = Student._meta.get_field('nobp').formfield()

    class Meta(RegistrationForm.Meta):
        model = MyUser
        fields = [
            User.USERNAME_FIELD,
            'email',
            'password1',
            'password2',
            'nobp'
        ]
        required_css_class = 'required'

    def clean(self):
        super(StudentRegistrationForm, self).clean()

        # Manually validate nobp
        # try:
        #     Student.NOBPVALIDATOR(self.cleaned_data['nobp'])
        # except ValidationError as err:
        #     raise ValidationError({'nobp': err.message})

        # Check unique nobp
        if Student.objects.filter(nobp=self.cleaned_data['nobp']).exists():
            raise ValidationError({
                'nobp': _("User with with the same no.bp you "
                          "entered has regitered.")
            })

    def save(self, commit=True):
        user = super(StudentRegistrationForm, self).save(commit)
        user.save()
        courses = Course.objects.all()
        course = None
        for c in courses:
            count = len(c.student_set.all())
            if c.capacity > count:
                course = c
        Student.objects.get_or_create(
            user=user,
            nobp=self.cleaned_data['nobp'],
            belong_in=course
        )
        return user
