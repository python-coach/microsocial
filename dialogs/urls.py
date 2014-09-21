# coding=utf-8
from __future__ import absolute_import
from django.conf.urls import url
from dialogs.views import DialogView


urlpatterns = [
    url(
        r'^messages/$',
        DialogView.as_view(),
        name='messages'
    ),
    url(
        r'^messages/(?P<user_id>\d+)/$',
        DialogView.as_view(),
        name='messages'
    ),
]
