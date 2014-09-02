# coding=utf-8
from __future__ import absolute_import
from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib.auth.views import logout
from auths.views import RegistrationView, PasswordRecoveryView, RegistrationConfirmView


urlpatterns = patterns(
    'auths.views',
    url(
        r'^login/$',
        'login_view',
        name='login'
    ),
    url(
        r'^logout/$',
        logout,
        {'next_page': settings.LOGIN_URL},
        name='logout'
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
