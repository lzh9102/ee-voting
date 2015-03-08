from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from .models import *

class LoginRequiredMixin:

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

VOTING_EVENT_FIELDS = ['title', 'description', 'starting_date', 'expiration_date']

class VotingEventList(LoginRequiredMixin, ListView):
    model = VotingEvent
    template_name = 'voting/voting_event_list.html'

class VotingEventCreate(LoginRequiredMixin, CreateView):
    model = VotingEvent
    fields = VOTING_EVENT_FIELDS
    template_name = 'voting/voting_event_create.html'

    def get_success_url(self):
        return self.object.url_edit

class VotingEventEdit(LoginRequiredMixin, UpdateView):
    model = VotingEvent
    fields = VOTING_EVENT_FIELDS
    template_name = 'voting/voting_event_edit.html'
    success_url = reverse_lazy('voting_event_list')

class VotingEventDelete(LoginRequiredMixin, DeleteView):
    model = VotingEvent
    template_name = 'voting/voting_event_delete.html'
    success_url = reverse_lazy('voting_event_list')

CANDIDATE_FIELDS = ['full_name']

class CandidateCreate(LoginRequiredMixin, CreateView):
    model = Candidate
    fields = CANDIDATE_FIELDS
    template_name = 'voting/candidate_create.html'

    def form_valid(self, form):
        form.instance.event = VotingEvent.objects.get(pk=self.kwargs['event'])
        return super(CandidateCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CandidateCreate, self).get_context_data(**kwargs)
        context['voting_event'] = VotingEvent.objects.get(pk=self.kwargs['event'])
        return context

    def get_success_url(self, **kwargs):
        event = VotingEvent.objects.get(pk=self.kwargs['event'])
        return event.url_edit

class CandidateEdit(LoginRequiredMixin, UpdateView):
    model = Candidate
    fields = CANDIDATE_FIELDS
    template_name = 'voting/candidate_edit.html'

    def get_success_url(self, **kwargs):
        return self.object.event.url_edit

class CandidateDelete(LoginRequiredMixin, DeleteView):
    model = Candidate
    template_name = 'voting/candidate_delete.html'

    def get_success_url(self, **kwargs):
        event = self.object.event
        return event.url_edit
