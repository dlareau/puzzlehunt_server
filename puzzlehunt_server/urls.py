"""puzzlehunt_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as base_auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/$', RedirectView.as_view(url=reverse_lazy('admin:app_list', args=('huntserver',)))),
    url(r'^staff/$', RedirectView.as_view(url=reverse_lazy('admin:app_list', args=('huntserver',)))),
    url(r'^staff/', admin.site.urls),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('huntserver.urls', namespace="huntserver")),
    url(r'^accounts/logout/$', base_auth_views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    url(r'^accounts/login/$', base_auth_views.LoginView.as_view()),
    url(r'^password_reset/$', base_auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', base_auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        base_auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', base_auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# Use silk if enabled
if 'silk' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^silk/', include('silk.urls', namespace='silk')))

# Hack for using development server
if(settings.DEBUG):
    import debug_toolbar
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
