#!/bin/env python3

import datetime
import re
import sys
from xml.dom import Node
import html5lib
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import ugettext as _
from ...models import SyncLog, ClanMember
from ... import sc2player

CLAN_MEMBER_TABLE_ID = 'ladderData'

# The name is located at the tird column of a row
NAME_COL = 2

# Use this regular expression to get the battle.net ID from the link wrapping the clan members's name.
BNET_ID_REGEX = re.compile('http://eu\.battle\.net/sc2/en/profile/(\d+)/(\d+)/\w+/')

# Use this integer to check if the battle.net ID provided is the real one.
NO_BNET_ID = 0


class Command(BaseCommand):
    """ Sync players with the specified clan tag from rankedftw to the database
    Existing members are names are updated while removed members' is_member property gets set to false to not break
    database integrity"""
    help = 'Syncs clan members from rankedftw.com with the database'
    _rankedftw_response = None
    clan_members = []
    time_started = None
    log = SyncLog(action=SyncLog.CLAN_MEMBER_SYNC)

    @staticmethod
    def _parse_member_detais(row):
        """ Takes a row from the clan member table, which is an Element object, fetches the member details and returns
        them as a dict.
        :return: Dict of member details
        """
        m = dict()
        cells = []

        # Filter only <td> tags
        for n in row.childNodes:
            if n.nodeType == Node.ELEMENT_NODE:
                cells.append(n)

        # Get name element
        name = cells[NAME_COL].getElementsByTagName('a')[0]
        name.normalize()

        # First element is clantag <span>, second is the actual name
        m['name'] = name.childNodes[1].nodeValue.strip()

        # Get battle.net ID from name Element via regex
        bnet_id_match = re.search(BNET_ID_REGEX, name.getAttribute('href'))

        if bnet_id_match is None:
            m['bnet_id'] = NO_BNET_ID
            m['region'] = 1
        else:
            m['bnet_id'] = bnet_id_match.groups()[0]
            m['region'] = bnet_id_match.groups()[1]

        return m

    def _parse_rankedftw_response(self):
        """ Takes nios.kr response and parses it to python objects
        :return: List of dictionaries of clan members
        """

        clan_member_table = None

        if self._rankedftw_response is None:
            return

        # HTML5Lib parses HTML text into a xml.etree.ElementTree instance
        dom = html5lib.parse(
            self._rankedftw_response.text,
            treebuilder='dom'
        )

        # Get all tables
        tables = dom.getElementsByTagName('table')

        if len(tables) == 0:
            return

        # Look for the table containing clan members
        for table in tables:
            if table.getAttribute('id') == CLAN_MEMBER_TABLE_ID:
                clan_member_table = table
                break

        if clan_member_table is None:
            self.stderr.write(_('Clan member table wasn\'t found in response from nios'))
            return

        members = clan_member_table.getElementsByTagName('tbody')[0].getElementsByTagName('tr')

        for member in members:
            self.clan_members.append(self._parse_member_detais(member))

        self.stdout.write('Finished processing HTML from rankedftw.com, beginning to sync with the database.')

        if settings.DEBUG:
            self.stdout.write(
                (_('Time spent so far - %f seconds' % (
                    (datetime.datetime.now() - self.time_started).total_seconds()
                )))
            )

    def handle(self, *args, **options):
        self.time_started = datetime.datetime.now()
        try:
            rankedftw_url = ('http://www.rankedftw.com/clan/%s/ladder-rank/' % settings.SC2_CLANMANAGER_CLAN_TAG)
        except AttributeError:
            self.stderr.write(_('SC2_CLANMANAGER_CLAN_TAG is undefined in settings. Exiting!'))
            sys.exit(1)

        self.stdout.write(_('Fetching clan members from rankedftw.com.'))

        try:
            self._rankedftw_response = requests.get(rankedftw_url, timeout=10)
        except requests.exceptions.Timeout:
            self.stderr.write(_('Request timed out. Exiting!'))
            self.log.notes = 'Request timed out'
            self.log.save()
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            self.stderr.write(_('Error performing request. Exiting!'))
            self.log.notes = 'Connection error'
            self.log.save()
            sys.exit(1)

        if self._rankedftw_response.status_code != 200:
            self.stderr.write(_('Invalid response from rankedftw. Exiting!'))
            self.log.notes = 'Response from rankedftw wasn\'t successful'
            self.log.save()
            sys.exit(1)

        if settings.DEBUG:
            self.stdout.write(
                (_('Request took %f seconds to finish' % (
                    (datetime.datetime.now() - self.time_started).total_seconds()
                )))
            )

        self.stdout.write(_('Clans received successfully! Scraping members!'))
        self._parse_rankedftw_response()

        if not self.clan_members:
            self.stdout.write(_('No members to process. Exiting!!'))
            self.log.notes = 'No members to process'
            self.log.save()
            sys.exit(0)

        existing_members = ClanMember.objects.all()

        for m in self.clan_members:
            # Check if member exists, if it doesn't, then fetch necessary data from battle net and create it
            member_name = m['name']

            try:
                # We check by bnet ID, because while the name can change, the ID can not.
                member_obj = existing_members.get(bnet_id=m['bnet_id'])
                if not member_obj.name_locked:
                    member_obj.name = member_name  # Update name in case player has changed it

                protected = member_obj.membership_status_locked or\
                    (timezone.now().date() - member_obj.join_date).days < ClanMember.STATUS_PROTECTION_DAYS

                if not member_obj.is_member and not protected:
                    member_obj.is_member = True
                    self.stdout.write(_('Marking %s as a member again!' % member_name))
                else:
                    self.stdout.write(_('Skipping %s' % member_name))

                member_obj.save()
                continue

            except ClanMember.DoesNotExist:
                # Member doesn't exist, add record
                self.stdout.write(
                    _('New member %s found. Querying battle.net and adding to database on success.' % member_name)
                )

                try:
                    new_member = sc2player.SC2Player(member_name, m['bnet_id'], m['region'])
                except sc2player.SC2PlayerException as e:
                    if e.type != sc2player.SC2PlayerException.STATUS_CODE:
                        # It can be the player just having their nickname changed, therefore returning a 404
                        msg = 'Getting player\'s details from battle.net failed: %s' % e
                        self.stderr.write(str(e))
                        self.log.notes = msg
                        self.log.save()
                        sys.exit(1)
                    continue

                # Save to database with the properties returned by SC2Player
                ClanMember(
                    name=new_member.name,
                    bnet_id=new_member.bnet_id,
                    region=new_member.region,
                    ladder_name=new_member.ladder_name,
                    ladder_id = new_member.ladder_id,
                    league=new_member.league,
                    race=new_member.race,
                    last_game=new_member.last_game.date(),
                    wins=new_member.wins,
                    losses=new_member.losses,
                    score=new_member.points,
                    rank=new_member.rank,
                ).save()

        self.stdout.write(
            _('Process finished successfully in %f seconds!' % (
                datetime.datetime.now() - self.time_started).total_seconds()
              )
        )
        self.log.success = True
        self.log.save()
