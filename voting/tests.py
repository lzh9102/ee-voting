from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime
from .models import *

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
