#!/bin/env python3

from django.conf.urls import url
from . import views

urlpatterns = [
    # Member list related
    url(r'^$', views.MemberView.as_view(), name='member_list'),
]
