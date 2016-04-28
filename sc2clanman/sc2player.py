#!/bin/env
# -*- coding: utf-8 -*-

import datetime
import requests
from . import models
from django.conf import settings
from django.utils import timezone


class SC2PlayerException(Exception):
    """Exception thrown on failure to get SC2Player details from battle.net API"""

    # List of possible types for the exception
    SETTINGS = 0
    TIMEOUT = 1
    CONN_ERR = 2
    STATUS_CODE = 3
    JSON_DECODE = 4

    def __init__(self, *args, **kwargs):
        self.type = kwargs.pop('type')
        super(SC2PlayerException, self).__init__(*args, **kwargs)


class SC2Player(object):
    """Get SC2 player stats from battle.net API"""

    BNET_LADDER_LIST_URL = 'https://eu.api.battle.net/sc2/profile/{}/{}/{}/ladders'
    BNET_LADDER_URL = 'https://eu.api.battle.net/sc2/ladder/{}'
    BNET_MATCH_HISTORY_URL = 'https://eu.api.battle.net/sc2/profile/{}/{}/{}/matches'

    # Matchmaking queue denoting the solo ladder
    SOLO_LADDER = 'LOTV_SOLO'

    # If the player hasn't played a solo game in the last 25 games, we just set the last game to the beginning of
    # the epoch.
    NO_LAST_GAME_DATE = datetime.datetime.fromtimestamp(0)

    NO_LADDER_ID = -1

    def __init__(self, name, bnet_id, region):
        super(SC2Player, self).__init__()
        self.name = name
        self.bnet_id = bnet_id
        self.region = region
        self.ladder_id = self.NO_LADDER_ID
        self.ladder_name = ''
        self.last_game = self.NO_LAST_GAME_DATE
        self.unranked = False
        self.league = 'BRONZE'
        self.race = models.ClanMember.RACE_RANDOM
        self.last_game = timezone.now()
        self.wins = 0
        self.losses = 0
        self.points = models.ClanMember.SCORE_UNRANKED
        self.rank = 100
        self.tag = settings.SC2_CLANMANAGER_CLAN_TAG  # Presume still a member

        try:
            api_key = settings.SC2_CLANMANAGER_BNET_API_KEY
        except AttributeError:
            raise SC2PlayerException(
                'SC2_CLANMANAGER_BNET_API_KEY not found in settings.py!',
                type=SC2PlayerException.SETTINGS
            )

        request_params = dict(
            locale='en_GB',
            apikey=api_key,
        )

        # Request player ladder details from battle.net
        try:
            self.bnet_response = requests.get(
                self.BNET_LADDER_LIST_URL.format(self.bnet_id, self.region, self.name),
                request_params, timeout=10
            )
        except requests.exceptions.Timeout:
            raise SC2PlayerException(
                'Request timed out while trying to fetch ladder list for %s!' % self.name,
                type=SC2PlayerException.TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            raise SC2PlayerException(
                'Connection error while trying to fetch ladder list for %s!' % self.name,
                type=SC2PlayerException.CONN_ERR
            )
        if self.bnet_response.status_code != 200:
            raise SC2PlayerException(
                'Unsuccessful response while trying to fetch ladder list for %s!' % self.name,
                type=SC2PlayerException.STATUS_CODE
            )

        try:
            current_season = self.bnet_response.json()['currentSeason']
        except ValueError:
            raise SC2PlayerException(
                    'Ladder list response from battle.net for %s wasn\'t JSON!' % self.name,
                    type=SC2PlayerException.JSON_DECODE
                )

        # Response seems to be successful, let's find the solo season and query it.
        for ladder in current_season:
            # In case the player has played solo ladder in other expansions, we need to find the correct one
            for ladder_type in ladder['ladder']:
                if ladder_type['matchMakingQueue'] == self.SOLO_LADDER:
                    self.ladder_id = ladder_type['ladderId']
                    self.ladder_name = ladder_type['ladderName']
                    self.wins = ladder_type['wins']
                    self.losses = ladder_type['losses']
                    self.league = ladder_type['league']
                    break

            if self.ladder_id != self.NO_LADDER_ID:
                break

        if self.ladder_id == self.NO_LADDER_ID:
            # A ladder containing this player wasn't found so we presume they're unranked.
            self.unranked = True
            return

        # We got most of what we need, now we unfortunately need to query the specific ladder the player is in
        # to get the ladderpoints and race
        try:
            self.ladder_response = requests.get(
                self.BNET_LADDER_URL.format(self.ladder_id),
                request_params, timeout=10
            )
        except requests.exceptions.Timeout:
            raise SC2PlayerException(
                'Request timed out while trying to fetch ladder details for %s!' % self.name,
                type=SC2PlayerException.TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            raise SC2PlayerException(
                'Connection error while trying to fetch ladder details for %s!' % self.name,
                type=SC2PlayerException.CONN_ERR
            )
        if self.ladder_response.status_code != 200:
            raise SC2PlayerException(
                'Unsuccessful response while trying to fetch ladder details for %s!' % self.name,
                type=SC2PlayerException.STATUS_CODE
            )

        try:
            ladder = self.ladder_response.json()['ladderMembers']
        except ValueError:
            raise SC2PlayerException(
                'Ladder details response from battle.net for %s wasn\'t JSON!' % self.name,
                type=SC2PlayerException.JSON_DECODE
            )

        # Response successful, proceed, look for the player
        for i, player in enumerate(ladder):
            if player['character']['displayName'] == self.name:
                self.points = int(player['points'])
                self.tag = player['character']['clanTag']  # So we can routinely check, if the player is still a member.
                # In rare cases, the ladder object doesn't contain a race. In that case we presume RANDOM
                try:
                    self.race = player['favoriteRaceP1']
                except KeyError:
                    self.race = models.ClanMember.RACE_RANDOM
                self.rank = i + 1
                break

        # Now we need the last played game date. For that we need to query the match history of the player.
        try:
            self.ladder_response = requests.get(
                self.BNET_MATCH_HISTORY_URL.format(self.bnet_id, self.region, self.name),
                request_params, timeout=10
            )
        except requests.exceptions.Timeout:
            raise SC2PlayerException(
                'Request timed out while trying to fetch match history for %s!' % self.name,
                type=SC2PlayerException.TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            raise SC2PlayerException(
                'Connection error while trying to fetch match history for %s!' % self.name,
                type=SC2PlayerException.CONN_ERR
            )
        if self.ladder_response.status_code != 200:
            raise SC2PlayerException(
                'Unsuccessful response while trying to fetch match history for %s!' % self.name,
                type=SC2PlayerException.STATUS_CODE
            )

        try:
            match_history = self.ladder_response.json()['matches']
        except ValueError:
            raise SC2PlayerException(
                'Match history response from battle.net for %s wasn\'t JSON!' % self.name,
                type=SC2PlayerException.JSON_DECODE
            )

        # Since it contains all games, we need to look for a solo game. Games are ordered by most recent first
        for match in match_history:
            if match['type'] == 'SOLO':
                self.last_game = datetime.datetime.fromtimestamp(match['date'])
                break
