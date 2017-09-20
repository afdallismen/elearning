from django.conf.urls import url

from account import views


app_name = 'account'
urlpatterns = [
    url(r'^edit/$', views.edit, name="edit")
]
