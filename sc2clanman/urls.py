#!/bin/env python3

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.MemberView.as_view(), name='member-list'),
]
