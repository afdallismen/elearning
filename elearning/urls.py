"""elearning URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

import debug_toolbar
from registration.backends.hmac import views as regis_views

from account import views as account_views
from account.forms import StudentRegistrationForm
from main import views as main_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^account/$', account_views.detail, name='account_detail'),
    url(r'^account/register/$',
        regis_views.RegistrationView.as_view(
            form_class=StudentRegistrationForm),
        name='registration_register'),
    url(r'^account/', include('registration.backends.hmac.urls')),
    url(r'^sis/', include('sis.urls')),
    url(r'^$', main_views.index, name="index")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
