from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import *
from .forms import parse_voters

def login(client):
    credentials = {'username': 'hello', 'password': '1234'}
    User.objects.create_user(**credentials)
    client.login(**credentials)

class VotingEventTests(TestCase):

    def setUp(self):
        login(self.client)

        self.vote1 = VotingEvent.objects.create(title='vote1',
                                                expiration_date='2015-01-01 00:00:00')

    def testCreate(self):
        # GET
        response = self.client.get(reverse('voting_event_create'))
        self.assertTemplateUsed(response, 'voting/voting_event_create.html')

        # POST
        formdata = {
            'title': 'abcd',
            'description': '123',
            'starting_date': '2015-01-01 00:00:00',
            'expiration_date': '2015-01-02 00:00:00',
        }
        response = self.client.post(reverse('voting_event_create'), formdata)
        new_vote = VotingEvent.objects.get(title='abcd')
        self.assertRedirects(response, new_vote.url_edit)

    def testEdit(self):
        # GET
        response = self.client.get(self.vote1.url_edit)
        self.assertTemplateUsed(response, 'voting/voting_event_edit.html')

        # POST
        formdata = {
            'title': 'vote2',
            'description': 'vote2 - description',
            'starting_date': datetime(2015, 12, 23, 1, 2, 3),
            'expiration_date': datetime(2015, 12, 23, 2, 2, 3)
        }
        response = self.client.post(self.vote1.url_edit, formdata)
        self.assertRedirects(response, reverse('voting_event_list'))

        updated_event = VotingEvent.objects.get(pk=self.vote1.pk)
        self.assertEqual(updated_event.title, formdata['title'])
        self.assertEqual(updated_event.description, formdata['description'])
        self.assertEqual(updated_event.expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
                         formdata['expiration_date'].strftime('%Y-%m-%d %H:%M:%S'))

    def testDelete(self):
        # GET
        response = self.client.get(self.vote1.url_delete)
        self.assertTemplateUsed(response, 'voting/voting_event_delete.html')

        # POST
        response = self.client.post(self.vote1.url_delete, {})
        self.assertRedirects(response, reverse('voting_event_list'))
        self.assertEqual(VotingEvent.objects.filter(pk=self.vote1.pk).count(), 0)

    def testStatus(self):
        vote = VotingEvent.objects.create(title='vote1',
                                          expiration_date='2015-01-01 00:00:00')
        candidate1 = Candidate.objects.create(event=vote,
                                              full_name='Candidate1')
        candidate2 = Candidate.objects.create(event=vote,
                                              full_name='Candidate2')
        voter1 = Voter.objects.create(event=vote,
                                      full_name='voter1',
                                      username='voter1',
                                      choice=candidate1)
        voter2 = Voter.objects.create(event=vote,
                                      full_name='voter2',
                                      username='voter2',
                                      choice=candidate2)
        voter3 = Voter.objects.create(event=vote,
                                      full_name='voter3',
                                      username='voter3',
                                      choice=candidate2)
        voter4 = Voter.objects.create(event=vote,
                                      full_name='voter4',
                                      username='voter4') # not voted

        response = self.client.get(reverse('voting_event_status',
                                           kwargs={'pk': vote.pk}))
        self.assertIn('candidates', response.context)
        candidates = response.context['candidates']
        # candidate2 get more votes than candidate1
        self.assertEqual(candidates, [candidate2, candidate1])

        self.assertIn('not_voted_voters', response.context)
        self.assertEqual(list(response.context['not_voted_voters']), [voter4])

# TODO: enable this after implementing CRUD for Voter
#class VoterTests(TestCase):
#
#    def testCreateVoter(self):
#        event = VotingEvent.objects.create(title='vote1',
#                                           starting_date='2015-01-01',
#                                           expiration_date='2015-02-01')
#        voter = Voter.objects.create(event=event,
#                                     full_name='John Smith',
#                                     username='johnsmith')
#        self.assertEqual(voter.username, 'johnsmith')
#        self.assertTrue(len(voter.passphrase) > 0) # auto-generated passphrase

class CandidateTests(TestCase):

    def setUp(self):
        self.event = VotingEvent.objects.create(title='vote1',
                                                starting_date='2015-01-01',
                                                expiration_date='2015-02-01')
        self.candidate1 = Candidate.objects.create(event=self.event,
                                                   full_name='candidate1')
        self.candidate2 = Candidate.objects.create(event=self.event,
                                                   full_name='candidate2')
        self.voter1 = Voter.objects.create(event=self.event,
                                           full_name='voter1',
                                           username='voter1',
                                           choice=self.candidate1)
        self.voter2 = Voter.objects.create(event=self.event,
                                           full_name='voter2',
                                           username='voter2',
                                           choice=self.candidate2)
        login(self.client)

    def testCandidateCreate(self):
        candidate_create_url = reverse('candidate_create', kwargs={'event': self.event.pk})
        # GET
        response = self.client.get(candidate_create_url)
        self.assertEqual(response.context['voting_event'], self.event)

        # POST
        formdata = {
            'full_name': 'candidate3',
        }
        response = self.client.post(candidate_create_url, formdata)
        self.assertRedirects(response, self.event.url_edit)
        self.assertTrue(Candidate.objects.filter(full_name='candidate3').exists())
        new_candidate = Candidate.objects.get(full_name='candidate3')
        self.assertEqual(new_candidate.event, self.event)

    def testCandidateEdit(self):
        # GET
        response = self.client.get(self.candidate1.url_edit)
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post(self.candidate1.url_edit, {
            'full_name': 'new_name',
        })
        self.assertRedirects(response, self.event.url_edit)
        new_candidate = Candidate.objects.get(pk=self.candidate1.pk)
        self.assertEqual(new_candidate.full_name, 'new_name')

    def testCandidateDelete(self):
        # GET
        response = self.client.get(self.candidate1.url_delete)
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post(self.candidate1.url_delete, {})
        self.assertRedirects(response, self.event.url_edit)
        self.assertFalse(Candidate.objects.filter(pk=self.candidate1.pk).exists())

    def testModelGetVoters(self):
        self.assertEqual(self.candidate1.voters.all().count(), 1)
        self.assertEqual(self.candidate1.voters.all()[0], self.voter1)

class VoterTests(TestCase):

    def setUp(self):
        self.event1 = VotingEvent.objects.create(title='vote1',
                                                starting_date='2015-01-01',
                                                expiration_date='2015-02-01')
        self.candidate1 = Candidate.objects.create(event=self.event1,
                                                   full_name='candidate1')
        self.voter1 = Voter.objects.create(event=self.event1,
                                           full_name='Voter1',
                                           username='voter1')
        self.event2 = VotingEvent.objects.create(title='vote2',
                                                 starting_date='2015-01-01',
                                                 expiration_date='2015-02-01')
        self.candidate2 = Candidate.objects.create(event=self.event2,
                                                   full_name='candidate2')
        self.voter2 = Voter.objects.create(event=self.event2,
                                           full_name='Voter2',
                                           username='voter2')
        login(self.client)

    def testVoterModelVote(self):
        # should't have a default candidate
        self.assertEqual(self.voter1.choice, None)

        # vote for the candidate
        try:
            self.voter1.vote_for(self.candidate1)
        except:
            self.fail("voter.vote_for() is broken")

        # verify voter1 has chosen candidate1
        self.assertEqual(self.voter1.choice, self.candidate1)

        # voter2 belongs to vote2, candidate1 belongs to vote1
        # voter2 shouldn't be able to vote for candidate1
        self.assertRaises(ValidationError,
                          self.voter2.vote_for, self.candidate1),
        # voter2's choice is not changed by an error vote
        self.assertEqual(self.voter2.choice, None)

    def testParseVoters(self):
        result = parse_voters("  The First Voter voter1\nSecond Voter voter2 \n  \n ")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("The First Voter", "voter1"))
        self.assertEqual(result[1], ("Second Voter", "voter2"))

        # lines with only one token is incorrect
        self.assertRaises(Exception, parse_voters, "  \tid")

    # TODO: add tests for voter wizard

    def testListVoters(self):
        response = self.client.get(reverse('voter_list',
                                           kwargs={'event': self.event1.pk}))
        try:
            voters = response.context['voters']
        except:
            self.fail("'voters' should be in context")
        self.assertEqual(len(voters), 1) # event1 has one candidate

class VotingTests(TestCase):

    def setUp(self):
        login(self.client)

        self.event1 = VotingEvent.objects.create(title='vote1',
                                                 starting_date='2015-01-01',
                                                 expiration_date='2015-02-01')
        self.candidate1 = Candidate.objects.create(event=self.event1,
                                                   full_name='candidate1')
        self.candidate2 = Candidate.objects.create(event=self.event2,
                                                   full_name='candidate2')

    # TODO: test voting views
