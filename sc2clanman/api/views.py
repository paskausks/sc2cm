#!/bin/env python3

from django.http import JsonResponse
from django.views.generic import View
from django.utils.translation import ugettext as _
from .. import models


def api_response(data, data_kw, message=_('Success'), **kwargs):
    """
    Function for preserving the same style of responses across API
    :param data_kw: Keyword for the data object
    :param message: informative message
    :param data: any JSON serializable object
    :return: JsonResponse object
    """
    rv = dict(
        message=message
    )
    rv[data_kw] = data

    return JsonResponse(rv, **kwargs)


class PlayerView(View):
    """
    A view to look for a player by a keyword. If found, returns the most relevant result as a JSON serialized
    Player object.
    """
    def get(self, request, **kwargs):

        kw = kwargs.get('keyword', '')
        data_kw = 'player'

        try:
            # Return the first search result when looking for this player
            player = models.ClanMember.clanmembers.order_by('-name').filter(name__icontains=kw)[0].serialize()
        except IndexError:
            return api_response({}, data_kw, _('Player not found'), status=404)

        return api_response(player, data_kw)


class TopView(View):
    """
    A view which returns the top 10 players by ladderpoints.
    """
    def get(self, request, **kwargs):

        kw = kwargs.get('keyword', '')
        data_kw = 'players'

        # Return the first search result when looking for this player
        players = [
            p.serialize() for p in models.ClanMember.clanmembers.order_by('-score')[:10]
            ]

        return api_response(players, data_kw)
