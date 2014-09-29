# coding=utf-8
from __future__ import absolute_import
from django.contrib import admin
from dialogs.models import Dialog, Message


admin.site.register((Dialog, Message))
