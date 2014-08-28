# coding=utf-8
from __future__ import absolute_import
from django.conf.urls import patterns, url
from auths.views import RegistrationView, PasswordRecoveryView, RegistrationConfirmView


urlpatterns = patterns(
    'auths.views',
    url(
        r'^login/$',
        'login_view',
        name='login'
    ),
    url(
        r'^registration/$',
        RegistrationView.as_view(),
        name='registration'
    ),
    url(
        r'^registration/(?P<token>.+)/$',
        RegistrationConfirmView.as_view(),
        name='registration_confirm'
    ),
    url(
        r'^password-recovery/$',
        PasswordRecoveryView.as_view(),
        name='password_recovery'
    ),
)
