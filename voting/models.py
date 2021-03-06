from django.db import models, IntegrityError
from datetime import datetime, timedelta
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from datetime import datetime
import random, string

def default_starting_time():
    return datetime.now()

def default_expire_time():
    return datetime.now() + timedelta(days=30)

PASSPHRASE_LENGTH = 8
def generate_passphrase():
    return ''.join([random.choice(string.ascii_uppercase + string.digits)
                    for i in range(PASSPHRASE_LENGTH)])

VOTE_CHOICE = (
    ('A', _('Agree')),
    ('D', _('Disagree')),
)

class VotingEvent(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    starting_date = models.DateTimeField(default=default_starting_time,
                                         verbose_name=_("Starting Time"))
    expiration_date = models.DateTimeField(default=default_expire_time,
                                           verbose_name=_("Expiration Time"))
    allow_revote = models.BooleanField(default=False,
                                       verbose_name=("Allow users to vote again (overwriting previous results)"))

    @property
    def url_edit(self):
        return reverse('voting_event_edit', kwargs={'pk': self.pk})

    @property
    def url_delete(self):
        return reverse('voting_event_delete', kwargs={'pk': self.pk})

    @property
    def url_voters(self):
        return reverse('voter_list', kwargs={'event': self.pk})

    @property
    def is_expired(self):
        return self.expiration_date <= datetime.now()

class Candidate(models.Model):
    event = models.ForeignKey(VotingEvent, related_name='candidates')
    full_name = models.CharField(max_length=128, verbose_name=_("Full Name"))

    def __str__(self):
        return self.full_name

    @property
    def url_edit(self):
        return reverse('candidate_edit', kwargs={'pk': self.pk})

    @property
    def url_delete(self):
        return reverse('candidate_delete', kwargs={'pk': self.pk})

    @property
    def voters(self):
        return event.voters.filter(choice=self)

    @property
    def agree_votes(self):
        return Vote.objects.filter(candidate=self, choice='A')

    @property
    def disagree_votes(self):
        return Vote.objects.filter(candidate=self, choice='D')

class Voter(models.Model):
    event = models.ForeignKey(VotingEvent, related_name='voters')
    full_name = models.CharField(max_length=128, verbose_name=_("Full Name"))
    username = models.CharField(max_length=64, verbose_name=_("Username"))
    passphrase = models.CharField(max_length=128, default=generate_passphrase,
                                  verbose_name=_("Passphrase"))
    choices = models.ManyToManyField(Candidate, related_name='voters',
                                     through='Vote')

    # TODO: change the name of this function to 'set_choice'
    def vote_for(self, candidate, agree):
        assert(isinstance(candidate, Candidate))
        assert(type(agree) == bool)

        # should only vote for candidates in the same voting event
        if candidate.event != self.event:
            # FIXME: this should be IntegrityError
            raise ValidationError("candidate and voter doesn't belong to the same voting event")

        # get the vote relationship between voter and candidate
        (vote, created) = Vote.objects.get_or_create(voter=self, candidate=candidate)

        if agree:
            vote.choice = 'A'
        else:
            vote.choice = 'D'

        vote.save()

    def unvote(self, candidate):
        assert(isinstance(candidate, Candidate))
        if candidate.event != self.event:
            raise IntegrityError("candidate and voter don't belong to the same event")
        Vote.objects.filter(voter=self, candidate=candidate).delete()

    @property
    def voted(self):
        return self.choices.all().exists()

    @property
    def voted_time(self):
        if self.voted:
            return self.votes.all()[0].modified_time # TODO: find the latest time
        else:
            return None

class Vote(models.Model):
    voter = models.ForeignKey(Voter, related_name='votes')
    candidate = models.ForeignKey(Candidate, related_name='votes')
    choice = models.CharField(choices=VOTE_CHOICE, max_length=2)
    modified_time = models.DateTimeField(auto_now=True, auto_now_add=True)

    @property
    def agree(self):
        return self.choice == 'A'
