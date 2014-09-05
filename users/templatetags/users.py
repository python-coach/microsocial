# coding=utf-8
from __future__ import absolute_import
from django import template
from django.conf import settings


register = template.Library()


@register.filter
def get_avatar(user):
    try:
        return user.avatar.url
    except ValueError:
        return '%susers/img/empty_avatar.png' % settings.STATIC_URL
