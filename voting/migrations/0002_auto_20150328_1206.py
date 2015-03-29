# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(choices=[('A', 'Agree'), ('D', 'Disagree')], max_length=2)),
                ('candidate', models.ForeignKey(related_name='votes', to='voting.Candidate')),
                ('voter', models.ForeignKey(related_name='votes', to='voting.Voter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='voter',
            name='choice',
        ),
        migrations.AddField(
            model_name='voter',
            name='choices',
            field=models.ManyToManyField(to='voting.Candidate', through='voting.Vote', related_name='voters'),
            preserve_default=True,
        ),
    ]
