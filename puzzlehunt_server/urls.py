from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as base_auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy
from django.views.generic import RedirectView

urlpatterns = [
    # Admin redirections/views
    url(r'^admin/login/$', RedirectView.as_view(url=reverse_lazy(settings.LOGIN_URL),
                                                query_string=True)),
    url(r'^staff/login/$', RedirectView.as_view(url=reverse_lazy(settings.LOGIN_URL),
                                                query_string=True)),
    url(r'^admin/$', RedirectView.as_view(url=reverse_lazy('admin:app_list',
                                          args=('huntserver',)))),
    url(r'^staff/$', RedirectView.as_view(url=reverse_lazy('admin:app_list',
                                          args=('huntserver',)))),
    url(r'^staff/', admin.site.urls),
    url(r'^admin/', admin.site.urls),

    # All of the huntserver URLs
    url(r'^', include('huntserver.urls', namespace="huntserver")),

    # User auth/password reset
    url(r'^accounts/logout/$', base_auth_views.LogoutView.as_view(),
        name='logout', kwargs={'next_page': '/'}),
    url(r'^accounts/login/$', base_auth_views.LoginView.as_view()),
    url(r'^password_reset/$', base_auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', base_auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        base_auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', base_auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
]

# Use silk if enabled
if 'silk' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^silk/', include('silk.urls', namespace='silk')))

# Hack for using development server
if(settings.DEBUG):
    import debug_toolbar
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
