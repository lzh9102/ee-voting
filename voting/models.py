from django.db import models
from datetime import datetime, timedelta
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

def default_starting_time():
    return datetime.now()

def default_expire_time():
    return datetime.now() + timedelta(days=30)

class VotingEvent(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    starting_date = models.DateTimeField(default=default_starting_time,
                                         verbose_name=_("Starting Time"))
    expiration_date = models.DateTimeField(default=default_expire_time,
                                           verbose_name=_("Expiration Time"))

    @property
    def url_edit(self):
        return reverse('voting_event_edit', kwargs={'pk': self.pk})

    @property
    def url_delete(self):
        return reverse('voting_event_delete', kwargs={'pk': self.pk})

class Candidate(models.Model):
    event = models.ForeignKey(VotingEvent, related_name='candidates')
    full_name = models.CharField(max_length=128, verbose_name=_("Full Name"))

class Voter(models.Model):
    username = models.CharField(max_length=64, verbose_name=_("Username"), unique=True)
    full_name = models.CharField(max_length=128, verbose_name=_("Full Name"))
    passphrase = models.CharField(max_length=128, verbose_name=_("Passphrase"))

class Vote(models.Model):
    event = models.ForeignKey(VotingEvent, related_name='votes')
    voter = models.ForeignKey(Voter, related_name='votes')
    choice = models.ForeignKey(Candidate, related_name='votes',
                               blank=True, null=True, on_delete=models.SET_NULL)
