#!/bin/env python3

from django.contrib import admin
from django.utils.translation import ugettext as _
from .. import models

"""
Modeladmins, actions and other functions for the ClanWar model.
"""


class ClanWarPlayerInline(admin.TabularInline):
    """
    Tabular InlineModelAdmin so clan war players can be edited straight from the clan war change form
    """
    model = models.ClanWarPlayer

    verbose_name = _('Player')
    verbose_name_plural = _('Players')
    show_change_link = True


class ClanWarAdmin(admin.ModelAdmin):
    """ModelAdmin for the ClanWar model"""

    inlines = [
        ClanWarPlayerInline
    ]

    exclude = [
        'players'
    ]

