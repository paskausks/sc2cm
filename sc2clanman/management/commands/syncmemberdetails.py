#!/bin/env python3

import datetime
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from ...models import SyncLog, ClanMember
from ... import sc2player
import sys


class Command(BaseCommand):
    """ Goes over all of the members in the database and updates all of their details """
    help = 'Updates clan member details in database with data from battle.net'
    log = SyncLog(action=SyncLog.CLAN_MEMBER_DETAIL_SYNC)
    time_started = None

    def handle(self, *args, **options):

        clan_members = ClanMember.objects.filter(is_member=True)
        self.time_started = datetime.datetime.now()

        self.stdout.write(_('Updating clan member details'))

        for member in clan_members:
            try:
                m = sc2player.SC2Player(member.name, member.bnet_id, member.region)
            except sc2player.SC2PlayerException as e:
                if e.type != sc2player.SC2PlayerException.STATUS_CODE:
                    # It can be the player just having their nickname changed, therefore returning a 404
                    msg = 'Getting player\'s details from battle.net failed: %s' % e
                    self.stderr.write(str(e))
                    self.log.notes = msg
                    self.log.save()
                    sys.exit(1)
                continue
                
            member.ladder_name = m.ladder_name
            member.ladder_id = m.ladder_id
            member.league = m.league
            member.race = m.race
            member.last_game = m.last_game.date()
            member.wins = m.wins
            member.losses = m.losses
            member.score = m.points
            member.rank = m.rank
            member.save()

            self.stdout.write(_('%s successfully updated!' % member.name))

        self.stdout.write(
            _('Process finished successfully in %f seconds!' % (
                datetime.datetime.now() - self.time_started).total_seconds()
              )
        )
        self.log.success = True
        self.log.save()
