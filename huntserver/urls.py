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
from . import views
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView

urlpatterns = [
    # Info Pages
    url(r'^$', views.index, name='index'),
    url(r'^hunt/info/$', TemplateView.as_view(template_name="hunt_info.html"), name='current_hunt_info'),
    url(r'^previous-hunts/$', TemplateView.as_view(template_name="previous_hunts.html"), name='previous_hunts'),
    url(r'^resources/$', TemplateView.as_view(template_name="resources.html"), name='resources'),
    url(r'^contactus/$', TemplateView.as_view(template_name="contact_us.html"), name='contact_us'),

    # Hunt Pages
    url(r'^puzzle/(?P<puzzle_id>[0-9a-fA-F]{3})/$', views.puzzle, name='puzzle'),
    url(r'^hunt/(?P<hunt_num>[0-9]+)/$', views.hunt, name='hunt'),
    url(r'^hunt/current/$', views.current_hunt, name='current_hunt'),
    url(r'^stats/$', views.public_stats, name='public_stats'),
    url(r'^chat/$',  views.chat, name='chat'),
    url(r'^objects/$', views.unlockables, name='unlockables'),
    url(r'^registration/$', views.registration, name='registration'),
    url(r'^protected/(?P<file_path>.+)$', views.protected_static, name='protected_static'),

    # Staff pages
    url(r'^staff/queue/$', views.queue, name='queue'),
    url(r'^staff/progress/$', views.progress, name='progress'),
    url(r'^staff/charts/$', views.charts, name='charts'),
    url(r'^staff/chat/$',  views.admin_chat, name='admin_chat'),
    url(r'^staff/control/$',  views.control, name='control'),
    url(r'^staff/teams/$', RedirectView.as_view(url='/admin/huntserver/team/', permanent=False)),
    url(r'^staff/puzzles/$', RedirectView.as_view(url='/admin/huntserver/puzzle/', permanent=False)),
    url(r'^staff/emails/$', views.emails, name='emails'),
]
