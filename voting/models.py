from django.db import models
from datetime import datetime, timedelta
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
import random, string

def default_starting_time():
    return datetime.now()

def default_expire_time():
    return datetime.now() + timedelta(days=30)

PASSPHRASE_LENGTH = 8
def generate_passphrase():
    return ''.join([random.choice(string.ascii_uppercase + string.digits)
                    for i in range(PASSPHRASE_LENGTH)])

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

    @property
    def url_edit(self):
        return reverse('candidate_edit', kwargs={'pk': self.pk})

    @property
    def url_delete(self):
        return reverse('candidate_delete', kwargs={'pk': self.pk})

class Voter(models.Model):
    event = models.ForeignKey(VotingEvent, related_name='voters')
    full_name = models.CharField(max_length=128, verbose_name=_("Full Name"))
    username = models.CharField(max_length=64, verbose_name=_("Username"))
    passphrase = models.CharField(max_length=128, default=generate_passphrase,
                                  verbose_name=_("Passphrase"))
    choice = models.ForeignKey(Candidate, related_name='voters',
                               blank=True, null=True, on_delete=models.SET_NULL)

    def vote_for(self, candidate):
        assert(isinstance(candidate, Candidate))
        if candidate.event != self.event:
            raise ValidationError("candidate and voter doesn't belong to the same voting event")
        self.choice = candidate

    @property
    def voted(self):
        return self.choice != None
