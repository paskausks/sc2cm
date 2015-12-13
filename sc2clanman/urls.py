#!/bin/env python3

from django.conf.urls import url
from . import views

urlpatterns = [
    # Member list related
    url(r'^$', views.MemberView.as_view(), name='member_list'),

    # Practice related
    url(r'^practice/$', views.PracticeListView.as_view(), name='practice_list'),
    url(r'^practice/edit/(?P<practice_id>\d+)$', views.PracticeEditView.as_view(), name='practice_edit'),
]
