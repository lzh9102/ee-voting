# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0003_vote_modified_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='modified_date',
        ),
        migrations.AddField(
            model_name='vote',
            name='modified_time',
            field=models.DateTimeField(auto_now=True, default='2015-01-01 00:00:00', auto_now_add=True),
            preserve_default=False,
        ),
    ]
