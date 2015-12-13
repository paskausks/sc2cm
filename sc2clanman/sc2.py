from django.conf import settings


class Race(object):
    """A Starcraft 2 Race with an icon property"""

    RACE_ICON_URL = 'ico/race-{}.png'

    def __init__(self, race):

        if not race:
            race = 'unknown'

        self.race = race.title()
        self.icon = settings.STATIC_URL + self.RACE_ICON_URL.format(self.race.lower())

        return

    def __str__(self):
        return self.race


class League(object):
    """A Starcraft 2 league with an icon property"""

    LEAGUE_ICON_URL = 'ico/league-{}.png'

    def __init__(self, race):

        if not race:
            race = 'unknown'

        self.league = race.title()
        self.icon = settings.STATIC_URL + self.LEAGUE_ICON_URL.format(self.league.lower())
        return

    def __str__(self):
        return self.league

