from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, TemplateView, FormView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.contrib.formtools.wizard.views import SessionWizardView as MyWizardView
from .forms import *
from .models import *
import re

class LoginRequiredMixin:

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

VOTING_EVENT_FIELDS = ['title', 'description', 'starting_date', 'expiration_date',
                       'allow_revote']

class VotingEventList(LoginRequiredMixin, ListView):
    model = VotingEvent
    queryset = model.objects.all().order_by('-expiration_date')
    template_name = 'voting/voting_event_list.html'

class VotingEventCreate(LoginRequiredMixin, CreateView):
    model = VotingEvent
    fields = VOTING_EVENT_FIELDS
    template_name = 'voting/voting_event_create.html'
    context_object_name = 'event'

    def get_success_url(self):
        return self.object.url_edit

class VotingEventEdit(LoginRequiredMixin, UpdateView):
    model = VotingEvent
    fields = VOTING_EVENT_FIELDS
    template_name = 'voting/voting_event_edit.html'
    context_object_name = 'event'
    success_url = reverse_lazy('voting_event_list')

class VotingEventDelete(LoginRequiredMixin, DeleteView):
    model = VotingEvent
    template_name = 'voting/voting_event_delete.html'
    success_url = reverse_lazy('voting_event_list')
    context_object_name = 'event'

class VotingEventStatus(LoginRequiredMixin, DetailView):
    template_name = 'voting/voting_event_status.html'
    model = VotingEvent
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(VotingEventStatus, self).get_context_data(**kwargs)

        # sort candidates by number of obtained votes (descending)
        candidates = list(self.object.candidates.all())
        candidates.sort(key=lambda candidate: -candidate.voters.all().count())

        context['candidates'] = candidates
        return context

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

class VoterMixin(LoginRequiredMixin):

    def get_voting_event(self):
        return VotingEvent.objects.get(pk=self.kwargs['event'])

class AddVoterWizard(VoterMixin, MyWizardView):
    template_name = 'voting/add_voter_wizard.html'
    form_list = [AddVoterForm, AddVoterConfirmForm]

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

class VoterList(VoterMixin, ListView):
    template_name = 'voting/voter_list.html'
    context_object_name = 'voters'

    def get_queryset(self):
        self.event = self.get_voting_event()
        return Voter.objects.filter(event=self.event)

    def get_context_data(self, **kwargs):
        context = super(VoterList, self).get_context_data(**kwargs)
        context['event'] = self.get_voting_event()
        return context

# same os VoterList, but using a different template
class VotersPrint(VoterList):
    template_name = 'voting/voters_print.html'

# same as VotersPrint but with different template
class VotingResultPrint(VotersPrint):
    template_name = 'voting/voting_result_print.html'

# vote views
# these views don't require login

class WelcomePage(FormView):
    form_class = CheckInfoForm
    template_name = 'voting/welcome_page.html'

    def dispatch(self, request, *args, **kwargs):
        # redirect to voting page if session['voter_id'] is already set
        if 'voter_id' in self.request.session:
            return HttpResponseRedirect(reverse('vote'))
        return super(WelcomePage, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'username': '',
                'passphrase': ''}

    def form_valid(self, form):
        data = form.cleaned_data

        # find possible users with (username, passphrase)
        voters = Voter.objects.filter(username=data['username'],
                                      passphrase=data['passphrase'])
        if voters:
            # TODO: check for multiple voters with the same (username, passphrase)
            voter = voters[0]

            if voter.event.is_expired:
                error = _("Sorry, the voting event has expired.")
            elif (not voter.event.allow_revote) and voter.voted:
                error = _("You already voted and can't vote again!")
            else:
                self.request.session['voter_id'] = voter.pk
                return HttpResponseRedirect(reverse('vote'))
        else:
            error = _("The username or passphrase you input is invalid")

        # validation error, display the form again
        context = {
            'form': form,
            'error': error,
        }
        return render(self.request, self.template_name, context)



class VoteView(View):
    template_name = 'voting/vote.html'
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        # redirect to welcome_page if no voter information in session
        if 'voter_id' not in request.session:
            return HttpResponseRedirect(reverse('welcome_page'))
        try:
            voter = Voter.objects.get(pk=request.session['voter_id'])
        except Voter.DoesNotExist:
            self.clear_session();
            return HttpResponseRedirect(reverse('welcome_page'))

        # enforce expiration date
        if voter.event.is_expired:
            return HttpResponseRedirect(reverse('welcome_page'))

        return super(VoteView, self).dispatch(request, *args, **kwargs)

    def get_voter(self):
        return Voter.objects.get(pk=self.request.session['voter_id'])

    def get(self, request):
        voter = self.get_voter()
        return self.display_form(request)

    def display_form(self, request, error=None, default_choices=None):
        voter = self.get_voter()
        context = {
            'candidates': voter.event.candidates.all().order_by('pk'),
            'event': voter.event,
            'voter': voter,
            'error': error,
            'choices': default_choices,
        }
        return render(request, self.template_name, context)

    def display_confirm_page(self, request, choices):
        return render(request, 'voting/vote_confirm.html', {
            # Convert the choices dict to a tuple list (candidate, choice).
            # The tuple list is sorted by the candidate id
            # FIXME: this is not covered by the unit test
            'choices_tuple': sorted(list(choices.items()),
                                    key=lambda x: x[0].pk),
        })

    def clear_session(self):
        self.request.session.pop('voter_id', None)

    def post(self, request):
        # TODO: form display and validation should be extract to a form class
        voter = self.get_voter()

        choices = {}
        for choice in request.POST:
            match = re.match(r'^candidate_(?P<event>\d+)$', choice)
            if match:
                candidate_id = match.group('event')
                candidate = Candidate.objects.get(pk=candidate_id)
                choices[candidate] = request.POST[choice]

        if 'cancel' in request.POST: # user cancels, return to welcome page
            self.clear_session()
            return HttpResponseRedirect(reverse('welcome_page'))

        if not choices:
            return self.display_form(request,
                                     error=_("Please choose one candidate"))

        # check if the candidates are all in the same event
        for candidate in choices:
            if candidate.event != voter.event:
                return self.display_form(request,
                                         error=_("The candidate you chose doesn't belong to this vote!"))

        if 'confirm' in request.POST:
            for candidate in voter.event.candidates.all():
                if (candidate not in choices) or (choices[candidate] == 'N'): # not selected
                    voter.unvote(candidate)
                else:
                    agree = (choices[candidate] == 'A')
                    # vote
                    voter.vote_for(candidate, agree=agree)

            voter.save()

            self.clear_session()
            return render(request, 'voting/end_message.html')
        elif 'modify' in request.POST:
            return self.display_form(request, error=None,
                                     default_choices=choices)
        else: # not confirmed
            return self.display_confirm_page(request, choices)

