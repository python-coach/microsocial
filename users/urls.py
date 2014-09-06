# coding=utf-8
from __future__ import absolute_import
from django.conf.urls import url
from users.views import UserProfileView, UserSettingsView


urlpatterns = [
    url(
        r'^profile/(?P<user_id>\d+)/$',
        UserProfileView.as_view(),
        name='user_profile'
    ),
    url(
        r'^settings/$',
        UserSettingsView.as_view(),
        name='user_settings'
    ),
]
