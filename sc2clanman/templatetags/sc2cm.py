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
    :param member: models.Player object
    '''
    return dict(strikes=range(member.strikes))


@register.simple_tag
def active(path, pattern):
    '''
    A template tag used for checking if current view is the active one.
    This way we can hightlight the active menu item.
    :param pattern: Regex pattern which is used to look if current menu item is the active one
    :param path: HTTP request path
    '''
    import re
    if re.search(pattern, path):
        return 'active'
    return ''
