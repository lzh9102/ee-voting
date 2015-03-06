# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0003_auto_20150306_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votingevent',
            name='expiration_date',
            field=models.DateTimeField(verbose_name='Expiration Time'),
            preserve_default=True,
        ),
    ]
