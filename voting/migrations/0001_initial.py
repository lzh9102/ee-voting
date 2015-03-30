# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import voting.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('full_name', models.CharField(verbose_name='Full Name', max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('choice', models.CharField(max_length=2, choices=[('A', 'Agree'), ('D', 'Disagree')])),
                ('modified_time', models.DateTimeField(auto_now_add=True, auto_now=True)),
                ('candidate', models.ForeignKey(to='voting.Candidate', related_name='votes')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('full_name', models.CharField(verbose_name='Full Name', max_length=128)),
                ('username', models.CharField(verbose_name='Username', max_length=64)),
                ('passphrase', models.CharField(verbose_name='Passphrase', max_length=128, default=voting.models.generate_passphrase)),
                ('choices', models.ManyToManyField(to='voting.Candidate', related_name='voters', through='voting.Vote')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VotingEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(verbose_name='Title', max_length=256)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('starting_date', models.DateTimeField(verbose_name='Starting Time', default=voting.models.default_starting_time)),
                ('expiration_date', models.DateTimeField(verbose_name='Expiration Time', default=voting.models.default_expire_time)),
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
            model_name='vote',
            name='voter',
            field=models.ForeignKey(to='voting.Voter', related_name='votes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='event',
            field=models.ForeignKey(to='voting.VotingEvent', related_name='candidates'),
            preserve_default=True,
        ),
    ]
