#!/bin/env python3

from collections import Counter
from django.contrib.auth.decorators import login_required, permission_required
from django.db import models as dm
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import BaseListView
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from . import models, apps, sc2, mixins


class BaseView(TemplateView):
    """
    A TemplateView subclass which adds the Opts object to context.
    """

    current_model = 'clanmember'

    def get_context_data(self, **kwargs):
        ctx = super(BaseView, self).get_context_data(**kwargs)

        # Get links so we can display links to admin.
        class Opts(object):
            app_label = 'sc2clanman'
            model_name = self.current_model

        ctx['opts'] = Opts()

        return ctx


class AuthenticatedView(BaseView):
    """
    BaseView subclass with the login required decorator applied.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AuthenticatedView, self).dispatch(*args, **kwargs)


class ListView(BaseListView, BaseView):
    """
    Combines BaseView with capability to show a paginated object list
    """
    pass


class MemberView(ListView):
    """ Show the clanmembers in a list ordered by ladder score"""
    template_name = 'sc2clanman/members.html'

    # No ordering since it's done by the front-end
    queryset = models.ClanMember.objects.filter(is_member=True)

    def get_context_data(self, **kwargs):
        ctx = super(MemberView, self).get_context_data(**kwargs)
        ctx['last_member_update'] = models.SyncLog.objects.filter(
                action=models.SyncLog.CLAN_MEMBER_SYNC,
                success=True,
        ).order_by('-time')[0].time
        ctx['last_detail_update'] = models.SyncLog.objects.filter(
                action=models.SyncLog.CLAN_MEMBER_DETAIL_SYNC,
                success=True
        ).order_by('-time')[0].time

        # Calculate quick stats

        # Game stats - aggregate and sum wins and losses
        gp = self.queryset.aggregate(dm.Sum('wins'), dm.Sum('losses'))
        ctx['total_games_played'] = gp['wins__sum'] + gp['losses__sum']

        # Annotate games played and winrate for each member
        games_played = self.queryset.annotate(
                games_played=dm.F('wins') + dm.F('losses')
        ).order_by('games_played')

        ctx['least_games_played'] = games_played.filter(games_played__gt=0).first()
        ctx['most_games_played'] = games_played.order_by('-games_played').first()

        # Last game date
        ctx['least_passionate'] = self.queryset.order_by('last_game').first()

        # Most prominent league, country and race
        league_breakdown = Counter(
                self.queryset.exclude(score=models.ClanMember.SCORE_UNRANKED).values_list('league', flat=True)
        ).most_common()
        ctx['league_breakdown'] = (
            (sc2.League(l[0]), l[1]) for l in league_breakdown
        )

        ctx['country_breakdown'] = Counter(
                self.queryset.exclude(country='').values_list('country', flat=True)
        ).most_common()

        race_breakdown = Counter(
                self.queryset.exclude(score=models.ClanMember.SCORE_UNRANKED).values_list('race', flat=True)
        ).most_common(4)

        ctx['race_breakdown'] = (
            (sc2.Race(r[0]), r[1]) for r in race_breakdown
        )

        ctx['version'] = apps.ClanManConfig.version_id
        return ctx


class PracticeListView(ListView):
    """
    View for displaying a list of practice events
    """
    current_model = 'practiceevent'
    template_name = 'sc2clanman/practice.html'
    queryset = models.PracticeEvent.objects.all().order_by('-date')


class PracticeEditView(mixins.PermissionRequiredMixin, AuthenticatedView):
    """
    A view for creating and editing practice events.
    Only users which have permissions to create practice events can access this view (ex. staff)
    """
    template_name = 'sc2clanman/practice_detail.html'
    permission_required = 'practiceevent.can_change'

    # noinspection PyMethodOverriding
    def get(self, request, practice_id, **kwargs):
        ctx = self.get_context_data()
        ctx['event'] = get_object_or_404(models.PracticeEvent, id=practice_id)
        return render(request, self.template_name, ctx)
