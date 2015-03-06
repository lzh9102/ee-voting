from django.db import models
from django.utils.translation import ugettext_lazy as _

class VotingEvent(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    expiration_date = models.DateField(verbose_name=_("Expiration Date"))

class Candidate(models.Model):
    event = models.ForeignKey(VotingEvent)
    full_name = models.CharField(max_length=128, verbose_name=_("Full Name"))

class Voter(models.Model):
    username = models.CharField(max_length=64, verbose_name=_("Username"), unique=True)
    full_name = models.CharField(max_length=128, verbose_name=_("Full Name"))
    passphrase = models.CharField(max_length=128, verbose_name=_("Passphrase"))

class Vote(models.Model):
    event = models.ForeignKey(VotingEvent)
    voter = models.ForeignKey(Voter)
    choice = models.ForeignKey(Candidate, blank=True, null=True, on_delete=models.SET_NULL)
