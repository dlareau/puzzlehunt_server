"""puzzlehunt_server URL Configuration"""
from django.conf.urls import include
from django.urls import path, register_converter, re_path
from huntserver import hunt_views, auth_views, info_views, staff_views
from django.contrib.auth import views as base_auth_views
from django.views.generic.base import RedirectView
from django.contrib.flatpages import views

app_name = "huntserver"

class PuzzleConverter:
    regex = '[0-9a-fA-F]{3,5}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return  value

register_converter(PuzzleConverter, 'puzzle')

# Note: For a few reasons, all admin/staff pages are declared in admin.py

urlpatterns = [
    # Pages made with flatpages
    path('hunt-info/', views.flatpage, {'url': '/hunt-info/'}, name='current_hunt_info'),
    path('contact-us/', views.flatpage, {'url': '/contact-us/'}, name='contact_us'),

    # Info Flatpages
    path('info/', include('django.contrib.flatpages.urls')),

    # Auth and Accounts
    path('accounts/create/', auth_views.create_account, name='create_account'),
    path('login-selection/', auth_views.login_selection, name='login_selection'),
    path('shib/login', auth_views.shib_login, name='new_shib_account'),
    path('logout/', auth_views.account_logout, name='account_logout'),

    # Info Pages
    path('', info_views.index, name='index'),
    path('previous-hunts/', info_views.previous_hunts, name='previous_hunts'),
    path('registration/', info_views.registration, name='registration'),
    path('user-profile/', info_views.user_profile, name='user_profile'),

    # Hunt Pages
    path('puzzle/<puzzle:puzzle_id>/', hunt_views.puzzle_view, name='puzzle'),
    re_path(r'^(?P<file_path>puzzle/[0-9a-fA-F]{3,5}/.+)$', hunt_views.protected_static,
        name='protected_static_2'),
    path('hints/<puzzle:puzzle_id>/', hunt_views.puzzle_hint, name='puzzle_hint'),
    path(r'hunt/<int:hunt_num>/', hunt_views.hunt, name='hunt'),
    path('hunt/current/', hunt_views.current_hunt, name='current_hunt'),
    path('hunt/<int:hunt_num>/prepuzzle/', hunt_views.hunt_prepuzzle, name='hunt_prepuzzle'),
    path('prepuzzle/<int:prepuzzle_num>/', hunt_views.prepuzzle, name='prepuzzle'),
    path('hunt/current/prepuzzle/', hunt_views.current_prepuzzle, name='current_prepuzzle'),
    path('chat/', hunt_views.chat, name='chat'),
    path('chat/status/', hunt_views.chat_status, name='chat_status'),
    path('leaderboard/', hunt_views.leaderboard, name='leaderboard'),
    path('leaderboard/<str:criteria>/', hunt_views.leaderboard, name='leaderboard'),
    path('objects/', hunt_views.unlockables, name='unlockables'),
    path('protected/<path:file_path>', hunt_views.protected_static, name='protected_static'),

    re_path(r'^Shibboleth.sso/Logout', base_auth_views.LogoutView.as_view(), name='logout',
        kwargs={'next_page': '/'}),
    re_path(r'^Shibboleth.sso/Login', base_auth_views.LoginView.as_view()),
]
