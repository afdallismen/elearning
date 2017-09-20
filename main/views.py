from operator import itemgetter

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render

from sis.decorators import redirect_admin
from sis.models import Module, Assignment, AssignmentResult


@redirect_admin
def index(request):
    if request.user.is_authenticated:
        get = {}
        modules, assignments = [], []
        get['content'] = request.GET.get('content', False)

        pks = AssignmentResult.objects.filter(
            student=request.user.student).values('assignment')
        user_assignments = Assignment.objects.filter(pk__in=pks).values()

        if get['content'] == "module":
            modules = Module.objects.values()
        elif get['content'] == "assignment":
            get['assignment'] = request.GET.get('assignment', False)

            if get['assignment'] == 'followed':
                assignments = user_assignments
            elif get['assignment'] == 'unfollwed':
                assignments = Assignment.objects.exclude(
                    pk__in=pks).values()
            else:
                assignments = Assignment.objects.values()
        else:
            modules = Module.objects.values()
            assignments = Assignment.objects.values()

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
                contents.append(
                    {
                        'created_on': item['created_on'],
                        'instance_of': instance_of,
                        'item': item,
                    }
                )
            contents = sorted(contents,
                              key=itemgetter('created_on'),
                              reverse=True)
        contexts = {'contents': contents}
        return render(request, 'main/auth/index.html', contexts)

    else:
        form = AuthenticationForm()
        contexts = {'form': form}
        return render(request, 'main/index.html', contexts)
