#!/bin/env python3

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.MemberView.as_view(), name='member-list'),
    url(r'^practice/$', views.PracticeListView.as_view(), name='practice-list'),
]
