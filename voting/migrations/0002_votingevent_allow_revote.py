# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='votingevent',
            name='allow_revote',
            field=models.BooleanField(default=False, verbose_name='Allow users to vote again (overwriting previous results)'),
            preserve_default=True,
        ),
    ]
