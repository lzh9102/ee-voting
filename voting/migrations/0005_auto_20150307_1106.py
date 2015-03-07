# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import voting.models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_auto_20150306_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='votingevent',
            name='starting_date',
            field=models.DateTimeField(default=voting.models.default_starting_time, verbose_name='Starting Time'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='votingevent',
            name='expiration_date',
            field=models.DateTimeField(default=voting.models.default_expire_time, verbose_name='Expiration Time'),
            preserve_default=True,
        ),
    ]
