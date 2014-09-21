# coding=utf-8
from __future__ import absolute_import
from django.contrib import admin
from news.models import NewsItem


admin.site.register(NewsItem)
