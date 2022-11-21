from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import views as base_auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy, path, re_path
from django.views.generic import RedirectView
from huntserver.admin import huntserver_admin

admin.site = huntserver_admin

urlpatterns = [
    # Admin redirections/views
    path('admin/login/', RedirectView.as_view(url=reverse_lazy(settings.LOGIN_URL), query_string=True)),
    path('staff/login/', RedirectView.as_view(url=reverse_lazy(settings.LOGIN_URL), query_string=True)),
    path('staff/', admin.site.urls),
    path('admin/', admin.site.urls),

    # All of the huntserver URLs
    path('', include('huntserver.urls', namespace="huntserver")),

    # User auth/password reset
    path('accounts/logout/', base_auth_views.LogoutView.as_view(),
        name='logout', kwargs={'next_page': '/'}),
    path('accounts/login/', base_auth_views.LoginView.as_view()),
    path('password_reset/', base_auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', base_auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        base_auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', base_auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
]


# Use silk if enabled
if 'silk' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^silk/', include('silk.urls', namespace='silk')))

# Hack for using development server
if(settings.DEBUG):
    import debug_toolbar
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(re_path(r'^__debug__/', include(debug_toolbar.urls)))
