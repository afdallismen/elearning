from operator import itemgetter

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.utils import timezone

from sis.decorators import redirect_admin
from sis.models import Module, Assignment


@redirect_admin
def index(request):
    if request.user.is_authenticated:
        get = {}
        modules, assignments = [], []
        get['content'] = request.GET.get('content', False)

        if get['content'] == "module":
            modules = Module.objects.filter(
                courses__in=[request.user.student.belong_in.pk]).values()
        elif get['content'] == "assignment":
            get['assignment'] = request.GET.get('assignment', False)

            assignments = Assignment.objects.filter(
                status=1, courses__in=[request.user.student.belong_in.pk]
            ).values()
        else:
            modules = Module.objects.filter(
                courses__in=[request.user.student.belong_in.pk]).values()
            assignments = Assignment.objects.filter(
                status=1, courses__in=[request.user.student.belong_in.pk]
            ).values()

        items = list(modules) + list(assignments)
        contents = []
        if items:
            for item in items:
                instance_of = 'module'
                if 'category' in list(item.keys()):
                    instance_of = 'assignment'
                if instance_of == 'module':
                    attachments = Module.objects.get(
                        pk=item['id']).attachments.all()
                    item.update({'attachments': attachments})
                else:
                    category = Assignment.objects.get(
                        pk=item['id']).get_category_display
                    item.update({'category': category})
                contents.append({
                    'created_on': item['created_on'],
                    'instance_of': instance_of,
                    'item': item,
                })
            contents = sorted(
                contents,
                key=itemgetter('created_on'),
                reverse=True
            )
        now = timezone.now()
        exams = Assignment.objects.filter(
            status=1,
            courses__in=[request.user.student.belong_in.pk],
            due__range=(now, now + timezone.timedelta(hours=2))
        )
        contexts = {'contents': contents, 'exams': exams}
        return render(request, 'main/auth/index.html', contexts)

    else:
        form = AuthenticationForm()
        contexts = {'form': form}
        return render(request, 'main/index.html', contexts)
