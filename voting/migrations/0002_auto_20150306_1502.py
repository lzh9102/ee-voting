# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VotingEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('expiration_date', models.DateField(verbose_name='Expiration Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='event',
            field=models.ForeignKey(to='voting.VotingEvent'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vote',
            name='event',
            field=models.ForeignKey(to='voting.VotingEvent'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='VoteEvent',
        ),
    ]
