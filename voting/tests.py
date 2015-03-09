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
        self.candidate2 = Candidate.objects.create(event=self.event1,
                                                   full_name='candidate2')
        self.voter1 = Voter.objects.create(event=self.event1,
                                           username='voter1')
        self.voter2 = Voter.objects.create(event=self.event1,
                                           username='voter2')
        self.voter3 = Voter.objects.create(event=self.event1,
                                           username='voter3')

    def testWelcomePageReject(self):
        client = Client()

        # the welcome page doesn't require login
        response = client.get(reverse('welcome_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('voting/welcome_page.html')
        self.assertEqual(len(response.context['form'].errors), 0)

        # input a correct candidate and an incorrect passphrase
        response = client.post(reverse('welcome_page'), {
            'username': self.voter1.username,
            'passphrase': self.voter1.passphrase + '123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertNotEqual(len(response.context['form'].errors), 0)

        # input a correct passphrase and an incorrect voter
        response = client.post(reverse('welcome_page'), {
            'username': self.voter1.username + '123',
            'passphrase': self.voter1.passphrase,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertNotEqual(len(response.context['form'].errors), 0)

    def testVotingProcess(self):
        client = Client()

        # Input a correct voter/passphrase pair.
        response = client.post(reverse('welcome_page'), {
            'username': self.voter1.username,
            'passphrase': self.voter1.passphrase,
        }, follow=True)

        # Following the response, it should redirect to the voting page.
        self.assertRedirects(response, reverse('vote'))
        self.assertEqual(response.context['event'], self.event1)
        self.assertEqual(response.context['voter'], self.voter1)

        # Now the browser should be on the voting page.
        # If we now point the browser to the welcome_page again, it should
        # redirect to the same voting page.
        response = client.get(reverse('welcome_page'), follow=True)
        self.assertRedirects(response, reverse('vote'))
        self.assertEqual(response.context['voter'], self.voter1)

        # Submit without choosing a candidate. This should show the form again
        # with error messages
        response = client.post(reverse('vote'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'voting/vote.html')

        # Just in case, if the client submits multiple clients, it should also
        # be an error
        response = client.post(reverse('vote'), {
            'choice': [self.candidate1.pk, self.candidate2.pk]
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'voting/vote.html')

        # Vote for exactly one candidate (candidate2) should show the final message.
        response = client.post(reverse('vote'), {
            'choice': [self.candidate2.pk]
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'voting/end_message.html')

        # voter1.choice should be updated in the database
        voter1 = Voter.objects.get(pk=self.voter1.pk)
        self.assertEqual(voter1.choice, self.candidate2)

        # After that, the welcome page should not redirect anymore
        response = client.get(reverse('welcome_page'))
        self.assertEqual(response.status_code, 200)

        # The vote page should redirect back to the welcome page
        response = client.get(reverse('vote'))
        self.assertRedirects(response, reverse('welcome_page'))

    def testEmptyUsernameError(self):
        """ Submitting an empty username/password should throw an exception """
        client = Client()
        try:
            response = client.post(reverse('welcome_page'), {})
            self.assertEqual(response.status_code, 200)
        except:
            self.fail("welcome_page: empty username/password causes an error")
