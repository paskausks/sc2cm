#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Custom template tags and filters for sc2clanman.
'''

__author__ = "ICE, Pundurs"
__copyright__ = "Copyright 2014, KA2"

from django import template
register = template.Library()


@register.inclusion_tag('sc2clanman/strikes.html')
def show_strikes(member):
    '''
    Shows strikes as contextually colored balls depending on the amount of strikes.
    '''
    return dict(strikes=range(member.strikes))
