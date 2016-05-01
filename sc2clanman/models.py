import bleach
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models
from django.utils.formats import date_format
from django.utils.translation import ugettext as _
from django.utils import timezone
from django_countries.fields import CountryField


class ClanMemberManager(models.Manager):
    """
    This manager returns ClanMember objects whose is_member property is set to True
    """
    def get_queryset(self):
        return super(ClanMemberManager, self).get_queryset().filter(is_member=True)


class ClanMember(models.Model):
    """Model for clan member"""

    # If player's score is of this value - we know they are a clan member, but unranked.
    SCORE_UNRANKED = -1

    RACE_TERRAN = 'TERRAN'
    RACE_ZERG = 'ZERG'
    RACE_PROTOSS = 'PROTOSS'
    RACE_RANDOM = 'RANDOM'

    # For how many days after a member is added is it's status protected from being changed by management jobs.
    STATUS_PROTECTION_DAYS = 3

    name = models.CharField('player name', max_length=50, help_text=_(
        'In the Battle.net URL http://eu.battle.net/sc2/en/profile/3568824/1/pundurs/, '
        '<i>pundurs</i> is the player name.'
    ))
    bnet_id = models.IntegerField('battle.net ID', help_text=_(
        'In the Battle.net URL http://eu.battle.net/sc2/en/profile/3568824/1/pundurs/, '
        '<i>3568824</i> is the Battle.net ID.'
    ))
    region = models.IntegerField('region', default=1, help_text=_(
        'In the Battle.net URL http://eu.battle.net/sc2/en/profile/3568824/1/pundurs/, '
        '<i>1</i> is the region. It\'s <i>1</i> for most accounts.'
    ))
    ladder_name = models.CharField('division', max_length=50, editable=False, blank=True)
    ladder_id = models.IntegerField('division id', editable=False, default=0)
    country = CountryField(blank_label=_('(select country)'), blank=True)
    league = models.CharField('league', editable=False, max_length=12, choices=(
        ('BRONZE', _('Bronze')),
        ('SILVER', _('Silver')),
        ('GOLD', _('Gold')),
        ('PLATINUM', _('Platinum')),
        ('DIAMOND', _('Diamond')),
        ('MASTER', _('Masters')),
        ('GRANDMASTER', _('Grandmasters')),
    ))
    race = models.CharField('race', editable=False, max_length=10, choices=(
        (RACE_TERRAN, _('Terran')),
        (RACE_ZERG, _('Zerg')),
        (RACE_PROTOSS, _('Protoss')),
        (RACE_RANDOM, _('Random')),
    ))
    skype_id = models.CharField('skype', max_length=100, blank=True)
    last_game = models.DateField('last game', auto_now_add=True, editable=False)
    wins = models.IntegerField('wins', editable=False, default=0)
    losses = models.IntegerField('losses', editable=False, default=0)
    score = models.IntegerField('ladder points', editable=False, default=SCORE_UNRANKED)
    rank = models.IntegerField('rank in division', editable=False, default=100)
    join_date = models.DateField('date joined', auto_now_add=True)
    practice_register = models.CharField('practice register', max_length=1, choices=(
        ('Y', _('Yes')),
        ('N', _('No (No excuse)')),
        ('E', _('Explained')),
    ), default='Y')
    strikes = models.IntegerField('amount of strikes', default=0)
    notes = models.TextField('notes', blank=True, help_text=_(
        'You can use HTML. Allowed tags - %s.<br> Links will be made clickable automatically.' % ', '.join(['&lt;' + tag + '&gt;' for tag in bleach.ALLOWED_TAGS])
    ))
    twitch_username = models.CharField('Twitch username', max_length=100, blank=True)

    is_member = models.BooleanField('is clan member', default=True, help_text=_(
        'Uncheck this instead of deleting the member from the database, so you don\'t lose the extra data you added '
        'which you might need again in case the member re-joins the clan.'
    ))

    # Member won't be affected by sync with Nios.kr.
    name_locked = models.BooleanField('is name locked', default=False, help_text=_(
        'If this is enabled, the player\'s name won\'t be changed by sync jobs.<br><br>Example use case: Nios.kr lists '
        'a member with an old name, but you want to specify the new one, so the stats sync works.'
    ))
    membership_status_locked = models.BooleanField('is membership status locked', default=False, help_text=_(
        'If this is enabled, the player\'s status won\'t be changed by sync jobs.<br><br>Example use case: Nios.kr '
        'lists a member who actually isn\'t in the clan anymore, but keeps getting listed as one.<br> '
        '<strong>NOTE:</strong> You most likely won\'t need to use this if you add a member manually, since '
        'their status is locked for ' + str(STATUS_PROTECTION_DAYS) + ' days allowing Nios.kr to catch up!'
    ))

    is_staff = models.BooleanField('is staff', default=False, help_text=_(
      'Used for informative purposes only.'
    ))

    rankedftw_teamid = models.IntegerField(_('RankedFTW team id'), default=0, editable=False)

    objects = models.Manager()
    clanmembers = ClanMemberManager()

    @property
    def is_unranked(self):
        return self.score == self.SCORE_UNRANKED

    @property
    def winrate(self):
        if self.wins == 0 and self.losses == 0:
            return 0
        return round(100 / (self.wins + self.losses) * self.wins, 2)

    @property
    def is_winrate_positive(self):
        return self.winrate > 50

    @property
    def total_games(self):
        return self.wins + self.losses

    @property
    def days_since_last_game(self):
        return (timezone.now().date() - self.last_game).days

    @property
    def bnet_profile_url(self):
        return 'http://eu.battle.net/sc2/en/profile/{}/{}/{}/'.format(self.bnet_id, self.region, self.name)

    @property
    def bnet_ladder_url(self):
        return 'http://eu.battle.net/sc2/en/profile/{}/{}/{}/ladder/{}#current-rank'.format(
            self.bnet_id, self.region, self.name, self.ladder_id
        )

    @property
    def rankedftw_url(self):
        if not self.rankedftw_teamid:
            return ''
        return 'http://www.rankedftw.com/ladder/lotv/1v1/ladder-rank/?team={}'.format(
            self.rankedftw_teamid
        )

    @property
    def rankedftw_graph_url(self):
        if not self.rankedftw_teamid:
            return ''
        return 'http://www.rankedftw.com/team/{}/'.format(
            self.rankedftw_teamid
        )

    @property
    def twitch_url(self):
        if not self.twitch_username:
            return ''
        return 'http://twitch.tv/{}/'.format(self.twitch_username)

    @property
    def get_admin_url(self):
        # Get admin URL for specific object, AdminSite independent.
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,)
        )

    @property
    def bleached_notes(self):
        linkified = bleach.linkify(self.notes)
        return bleach.clean(linkified)

    def __str__(self):
        return self.name

    def serialize(self):
        """
        Returns JSON serializable dict of instance
        """
        return dict(
            name=self.name,
            bnet_id=self.bnet_id,
            region=self.region,
            ladder_name=self.ladder_name,
            ladder_id=self.ladder_id,
            country=self.get_country_display(),
            league=self.get_league_display(),
            race=self.get_race_display(),
            last_game=date_format(self.last_game, 'SHORT_DATE_FORMAT'),
            wins=self.wins,
            losses=self.losses,
            score=self.score,
            rank=self.rank,
            join_date=date_format(self.join_date, 'SHORT_DATE_FORMAT'),
            winrate=self.winrate,
            total_games=self.total_games,
            bnet_profile_url=self.bnet_profile_url,
            twitch_username=self.twitch_username,
            twitch_url=self.twitch_url,
            rankedftw_url=self.rankedftw_url,
            rankedftw_graph_url=self.rankedftw_graph_url
        )

    class Meta:
        verbose_name = 'player'
        verbose_name_plural = 'players'


class SyncLog(models.Model):
    """ A log entry for sync events triggered by management jobs"""
    # Identifiers for actions
    CLAN_MEMBER_SYNC = 'CM'
    CLAN_MEMBER_DETAIL_SYNC = 'CMD'

    action = models.CharField('identifier', max_length=3, choices=(
        (CLAN_MEMBER_SYNC, _('Clan member sync')),
        (CLAN_MEMBER_DETAIL_SYNC, _('Clan member detail sync')),
    ))
    time = models.DateTimeField('time', auto_now_add=True)
    notes = models.TextField('notes', blank=True)
    success = models.BooleanField('was operation successful?', default=False)

    class Meta:
        verbose_name = 'sync event'
        verbose_name_plural = 'sync events'

    def __str__(self):
        return self.get_action_display()


class ClanWar(models.Model):
    date = models.DateTimeField(_('Date and time'))
    opponent_name = models.CharField(_('Opponent'), max_length=50)
    game_channel = models.CharField(_('In game channel'), blank=True, max_length=50)
    players = models.ManyToManyField(
        ClanMember, verbose_name=_('Players'), through='ClanWarPlayer'
    )
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = 'clan war'
        verbose_name_plural = 'clan wars'
        ordering = ('-date',)

    def __str__(self):
        return '{} - {}'.format(date_format(self.date, 'SHORT_DATETIME_FORMAT'), self.opponent_name)

    @property
    def get_admin_url(self):
        # Get admin URL for specific object, AdminSite independent.
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,)
        )

    def serialize(self):
        """
        Returns JSON serializable dict of instance
        """
        return dict(
            id=self.id,
            datetime=date_format(self.date, 'SHORT_DATETIME_FORMAT'),
            opponent=self.opponent_name,
            ingame_channel=self.game_channel,
            players=[p.serialize() for p in self.players.all()],
            notes=self.notes
        )


class ClanWarPlayer(models.Model):
    player = models.ForeignKey(ClanMember, verbose_name=_('Player'), limit_choices_to={'is_member': True})
    clanwar = models.ForeignKey(ClanWar, verbose_name=_('Clan war'))

    class Meta:
        verbose_name = _('Clan war player')
        verbose_name_plural = _('Clan war players')
        unique_together = ('clanwar', 'player')
