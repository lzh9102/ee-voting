# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_auto_20150306_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='event',
            field=models.ForeignKey(related_name='candidates', to='voting.VotingEvent'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vote',
            name='choice',
            field=models.ForeignKey(to='voting.Candidate', on_delete=django.db.models.deletion.SET_NULL, related_name='votes', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vote',
            name='event',
            field=models.ForeignKey(related_name='votes', to='voting.VotingEvent'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vote',
            name='voter',
            field=models.ForeignKey(related_name='votes', to='voting.Voter'),
            preserve_default=True,
        ),
    ]
