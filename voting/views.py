from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.formtools.wizard.views import SessionWizardView as MyWizardView
from .forms import *
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

class RedirectToVotingEvent:

    def get_success_url(self, **kwargs):
        event = self.object.event
        return event.url_edit

# candidate views

CANDIDATE_FIELDS = ['full_name']

class CandidateMixin(LoginRequiredMixin, RedirectToVotingEvent):
    pass

class CandidateCreate(CandidateMixin, CreateView):
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

class CandidateEdit(CandidateMixin, UpdateView):
    model = Candidate
    fields = CANDIDATE_FIELDS
    template_name = 'voting/candidate_edit.html'

class CandidateDelete(CandidateMixin, DeleteView):
    model = Candidate
    template_name = 'voting/candidate_delete.html'

# voter views
# A voting event usually has a large number of eligible voters. Therefore, the
# voter-adding interface is implemented as a custom form that enables the
# administrator to add multiple voters quickly.

# VoterMixin = LoginRequiredMixin + RedirectToVotingEvent
class VoterMixin(LoginRequiredMixin, RedirectToVotingEvent):
    pass

class AddVoterWizard(LoginRequiredMixin, MyWizardView):
    template_name = 'voting/add_voter_wizard.html'
    form_list = [AddVoterForm, AddVoterConfirmForm]

    def get_voting_event(self):
        return VotingEvent.objects.get(pk=self.kwargs['event'])

    def get_success_url(self, **kwargs):
        return self.get_voting_event().url_edit

    def get_context_data(self, **kwargs):
        context = super(AddVoterWizard, self).get_context_data(**kwargs)
        context['voting_event'] = self.get_voting_event()

        # pass in the generated voters in the last step
        if self.steps.current == self.steps.last:
            data = self.get_cleaned_data_for_step('0')
            voters = parse_voters(data['voters_input']) # this step should't fail
            context['voters'] = voters

        return context

    def done(self, form_list, form_dict, **kwargs):
        voter_form = form_dict['0']
        event = self.get_voting_event()
        voter_form.save(voting_event=event)
        return HttpResponseRedirect(self.get_success_url())
