from django.conf.urls import url

from sis import views

app_name = 'sis'
urlpatterns = [
    url(r'^module/(?P<slug>[\w-]+)/$', views.module_detail,
        name="module_detail"),
    url(r'^assignment/(?P<pk>[0-9]+)/$', views.assignment_detail,
        name="assignment_detail"),
    url(r'^answer/(?P<pk>[0-9]+)/$', views.do_answer,
        name="do_answer"),
]
