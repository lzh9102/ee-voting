from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from .models import *

class LoginRequiredMixin:

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

class VotingEventList(LoginRequiredMixin, ListView):
    model = VotingEvent
    template_name = 'voting/voting_event_list.html'

class VotingEventCreate(LoginRequiredMixin, CreateView):
    model = VotingEvent
    fields = ['title', 'description', 'expiration_date']
    template_name = 'voting/voting_event_create.html'

    def get_success_url(self):
        return self.object.url_edit

class VotingEventEdit(LoginRequiredMixin, UpdateView):
    model = VotingEvent
    fields = ['title', 'description', 'expiration_date']
    template_name = 'voting/voting_event_edit.html'
    success_url = reverse_lazy('voting_event_list')

class VotingEventDelete(LoginRequiredMixin, DeleteView):
    model = VotingEvent
    template_name = 'voting/voting_event_delete.html'
    success_url = reverse_lazy('voting_event_list')
