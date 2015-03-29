from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    # voting events
    url(r'^voting_event_list$', VotingEventList.as_view(), name='voting_event_list'),
    url(r'^voting_event_create/?$', VotingEventCreate.as_view(), name='voting_event_create'),
    url(r'^voting_event_edit/(?P<pk>\d+)$', VotingEventEdit.as_view(), name='voting_event_edit'),
    url(r'^voting_event_delete/(?P<pk>\d+)$', VotingEventDelete.as_view(), name='voting_event_delete'),
    url(r'^voting_event_status/(?P<pk>\d+)$', VotingEventStatus.as_view(), name='voting_event_status'),

    # candidate
    url(r'^voting_event/(?P<event>\d+)/candidate_create/$', CandidateCreate.as_view(),
        name='candidate_create'),
    url(r'^candidate_edit/(?P<pk>\d+)$', CandidateEdit.as_view(),
        name='candidate_edit'),
    url(r'^candidate_delete/(?P<pk>\d+)$', CandidateDelete.as_view(),
        name='candidate_delete'),

    # voters
    url(r'^voting_event/(?P<event>\d+)/add_voter_wizard$', AddVoterWizard.as_view(),
        name='add_voter_wizard'),
    url(r'^voting_event/(?P<event>\d+)/voter_list$', VoterList.as_view(),
        name='voter_list'),
    url(r'^voting_event/(?P<event>\d+)/voters_print$', VotersPrint.as_view(),
        name='voters_print'),
    url(r'^voting_event/(?P<event>\d+)/voting_result_print$', VotingResultPrint.as_view(),
        name='voting_result_print'),

    # voting
    url(r'^$', WelcomePage.as_view(), name='welcome_page'),
    url(r'^vote$', VoteView.as_view(), name='vote'),
)
