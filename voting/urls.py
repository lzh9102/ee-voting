from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^$', VotingEventList.as_view(), name='voting_event_list'),
    url(r'^voting_event_create/?$', VotingEventCreate.as_view(), name='voting_event_create'),
    url(r'^voting_event_edit/(?P<pk>\d+)$', VotingEventEdit.as_view(), name='voting_event_edit'),
    url(r'^voting_event_delete/(?P<pk>\d+)$', VotingEventDelete.as_view(), name='voting_event_delete'),
)
