# coding=utf-8
from __future__ import absolute_import
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from users.models import UserWallPost, make_friends, break_friends


class NewsItemManager(models.Manager):
    def for_user(self, user):
        friends_ids = list(user.friends.values_list('pk', flat=True))
        friends_ids.append(user.pk)
        return self.filter(Q(user_id__in=friends_ids) | Q(target_id__in=friends_ids))


class NewsItem(models.Model):
    TYPE_WALL_POST = 'wall_post'
    TYPE_MAKE_FRIENDS = 'make_friends'
    TYPE_BREAK_FRIENDS = 'break_friends'
    TYPE_CHOICES = (
        (TYPE_WALL_POST, _(u'сообщение на стене')),
        (TYPE_MAKE_FRIENDS, _(u'создание дружественной связи')),
        (TYPE_BREAK_FRIENDS, _(u'разрыв дружественной связи')),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    target = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    news_object = GenericForeignKey()
    created = models.DateTimeField(auto_now_add=True)

    objects = NewsItemManager()

    def get_templte_for_display(self):
        return 'news/display_%s.html' % self.type

    class Meta:
        ordering = ('-created',)


@receiver(post_save, sender=UserWallPost)
def add_news_wall_post(sender, instance, **kwargs):
    NewsItem.objects.create(
        user=instance.user,
        target=instance.author,
        type=NewsItem.TYPE_WALL_POST,
        news_object=instance
    )


@receiver(make_friends)
def add_news_make_friends(sender, user1_id, user2_id, **kwargs):
    NewsItem.objects.create(
        user_id=user1_id,
        target_id=user2_id,
        type=NewsItem.TYPE_MAKE_FRIENDS,
    )


@receiver(break_friends)
def add_news_break_friends(sender, user1_id, user2_id, **kwargs):
    NewsItem.objects.create(
        user_id=user1_id,
        target_id=user2_id,
        type=NewsItem.TYPE_BREAK_FRIENDS,
    )
