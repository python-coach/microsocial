# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_friends'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_user', models.ForeignKey(related_name=b'outcoming_friend_invitations', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(related_name=b'incoming_friend_invitations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='friendinvitation',
            unique_together=set([('from_user', 'to_user')]),
        ),
    ]
