# coding=utf-8
from __future__ import absolute_import
from django.views.generic.base import TemplateView


class UserProfileView(TemplateView):
    template_name = 'users/profile.html'
