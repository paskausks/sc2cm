#!/bin/env python3

from django.contrib.admin import ModelAdmin
from django.utils.translation import ugettext as _
from ..models import SyncLog

"""
Modeladmins, actions and other functions for the SyncLog model.
"""


class SyncLogAdmin(ModelAdmin):
    """ModelAdmin for the SyncLog model"""
    date_hierarchy = 'time'
    list_display = ('time', 'action', 'success', 'notes')
    list_display_links = ('action',)
    list_filter = ('success', 'action')
    ordering = ('-time',)
    fields = ('time', 'notes', 'success')
    readonly_fields = ('time', 'success')
    search_fields = ('notes',)
