#!/bin/env python3

from django.conf.urls import url, include
from . import views, api

urlpatterns = [
    # Member list related
    url(r'^$', views.MemberView.as_view(), name='member_list'),
    url(r'^cw/$', views.ClanWarView.as_view(), name='clan_wars'),
    url(r'^cw/(?P<cw_id>\d+)$', views.ClanWarDetailView.as_view(), name='clan_war_detail'),
    url(r'^api$', views.BaseView.as_view(template_name='sc2clanman/api.html'), name='api_docs'),

    # API Namespace
    url(r'^api/', include('sc2clanman.api.urls', namespace='api')),
]
