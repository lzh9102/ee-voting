# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_auto_20150328_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='modified_date',
            field=models.DateField(auto_now_add=True, auto_now=True, default='2015-01-01'),
            preserve_default=False,
        ),
    ]
