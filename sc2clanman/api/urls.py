#!/bin/env python3

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^player/(?P<keyword>\w+)/$', views.PlayerView.as_view(), name='player'),
    url(r'^top$', views.TopView.as_view(), name='top'),
    url(r'^cw$', views.ClanWarView.as_view(), name='clan_wars'),
    url(r'^cw/(?P<cw_id>\d+)/$', views.ClanWarDetailView.as_view(), name='clan_war_detail'),
]
