from django.conf.urls import url

from chat import views


app_name = "chat"
urlpatterns = [
    url(r'^$', views.index, name="index")
]
