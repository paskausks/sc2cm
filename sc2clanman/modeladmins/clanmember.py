#!/bin/env python3

from django.contrib.admin import ModelAdmin
from django.utils.translation import ugettext as _
from django.utils.text import Truncator

"""
Modeladmins, actions and other functions for the ClanMember model.
"""


def make_members(modeladmin, request, queryset):
    """Mark queryset as clan members"""
    queryset.update(is_member=True)
make_members.short_description = _('Mark selected players as clan members')


def make_non_members(modeladmin, request, queryset):
    """Mark queryset as non-clan members"""
    queryset.update(is_member=False)
make_non_members.short_description = _('Mark selected players as not being clan members')


def lock_names(modeladmin, request, queryset):
    """Lock names of all ClanMembers in QuerySet"""
    queryset.update(name_locked=True)
lock_names.short_description = _('Lock names of selected players')


def unlock_names(modeladmin, request, queryset):
    """Unlock names of all ClanMembers in QuerySet"""
    queryset.update(name_locked=False)
unlock_names.short_description = _('Unlock names of selected players')


def lock_membership_statuses(modeladmin, request, queryset):
    """Lock membership statuses of all ClanMembers in QuerySet"""
    queryset.update(membership_status_locked=True)
lock_membership_statuses.short_description = _('Lock membership statuses of selected players')


def unlock_membership_statuses(modeladmin, request, queryset):
    """Unlock membership statuses of all ClanMembers in QuerySet"""
    queryset.update(membership_status_locked=False)
unlock_membership_statuses.short_description = _('Unlock membership statuses of selected players')


def get_trimmed_notes(obj):
    """
    :param obj: Object being show in change list row
    :return: trimmed note
    """
    return Truncator(obj.notes).chars(255)
get_trimmed_notes.short_description = _('Notes')


class ClanMemberAdmin(ModelAdmin):
    """ModelAdmin for the ClanMember model"""

    actions = [
        make_members,
        make_non_members,
        lock_names,
        unlock_names,
        lock_membership_statuses,
        unlock_membership_statuses
    ]

    fieldsets = (
        (_('Battle.net information'), {
            'fields': ('name', 'bnet_id', 'region'),
            'description': _('All the main information needed to sync player statistics from Battle.net.')
        }),
        (_('Clan specific'), {
            'fields': ('join_date', 'practice_register', 'strikes', 'notes', 'is_staff', 'is_member'),
        }),
        (_('Extra information'), {
            'fields': ('country', 'twitch_username', 'skype_id'),
        }),
        (_('Locks'), {
            'fields': ('name_locked', 'membership_status_locked'),
            'description': _('Protect details from being changed by sync events.')
        }),
        (_('Battle.net profile details'), {
            'fields': (
                'race', 'league', 'ladder_id', 'ladder_name', 'last_game', 'wins', 'losses', 'score', 'rank',

            ),
        }),
    )

    list_display = ('name', 'bnet_id', 'is_member', get_trimmed_notes)
    list_editable = ('is_member',)
    list_filter = ('is_member', 'is_staff', 'name_locked', 'membership_status_locked')

    ordering = ('name',)

    readonly_fields = (
        'join_date', 'race', 'league', 'ladder_id', 'ladder_name', 'rank', 'last_game', 'wins', 'losses', 'score'
    )

    search_fields = ('name', 'bnet_id')
