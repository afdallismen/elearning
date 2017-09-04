from django.conf.urls import url

from sis import views

app_name = 'sis'
urlpatterns = [
    url(r'^modules/$', views.index, name="module_index"),
    url(r'^modules/(?P<slug>[\w-]+)/$', views.detail, name="module_detail")
]
