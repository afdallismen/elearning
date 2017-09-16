from operator import itemgetter

from django.shortcuts import render

from registration.backends.hmac import views as regis_views

from account.forms import StudentRegistrationForm
from sis.models import Module, Assignment


def index(request):
    if request.user.is_authenticated:
        content = request.GET.get('c', False)
        if content == "m":
            modules = Module.objects.values()
        elif content == "a":
            assignments = Assignment.objects.values()
        else:
            modules = Module.objects.values()
            assignments = Assignment.objects.values()
        items = list(modules) + list(assignments)
        contents = []
        if items:
            for item in items:
                contents.append(
                    {
                        'created_on': item['created_on'],
                        'class': item.__class__.__name__,
                        'item': item
                    }
                )
            contents = sorted(contents,
                              key=itemgetter('created_on'),
                              reverse=True)

        return render(request, 'main/auth_index.html', {'contents': contents})
    else:
        form = StudentRegistrationForm()
        if request.method == "POST":
            return regis_views.RegistrationView.as_view(
                form_class=StudentRegistrationForm
            )(request)
        return render(request, 'main/index.html', {'form': form})
