# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=128, verbose_name='Full Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.ForeignKey(blank=True, null=True, to='voting.Candidate', on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VoteEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('expiration_date', models.DateField(verbose_name='Expiration Date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64, unique=True, verbose_name='Username')),
                ('full_name', models.CharField(max_length=128, verbose_name='Full Name')),
                ('passphrase', models.CharField(max_length=128, verbose_name='Passphrase')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='vote',
            name='event',
            field=models.ForeignKey(to='voting.VoteEvent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vote',
            name='voter',
            field=models.ForeignKey(to='voting.Voter'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='event',
            field=models.ForeignKey(to='voting.VoteEvent'),
            preserve_default=True,
        ),
    ]
