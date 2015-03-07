# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import voting.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('full_name', models.CharField(max_length=128, verbose_name='Full Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('full_name', models.CharField(max_length=128, verbose_name='Full Name')),
                ('username', models.CharField(max_length=64, verbose_name='Username')),
                ('passphrase', models.CharField(max_length=128, default=voting.models.generate_passphrase, verbose_name='Passphrase')),
                ('choice', models.ForeignKey(to='voting.Candidate', null=True, blank=True, related_name='voters', on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VotingEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('starting_date', models.DateTimeField(default=voting.models.default_starting_time, verbose_name='Starting Time')),
                ('expiration_date', models.DateTimeField(default=voting.models.default_expire_time, verbose_name='Expiration Time')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='voter',
            name='event',
            field=models.ForeignKey(to='voting.VotingEvent', related_name='voters'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='event',
            field=models.ForeignKey(to='voting.VotingEvent', related_name='candidates'),
            preserve_default=True,
        ),
    ]
