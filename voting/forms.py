from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Voter
import re

def parse_voters(text):
    """ Parse the input and get a list of (Full Name, ID)

        The input consists of multiple lines, each line is in the format
        "<name> <id>", separated by spaces. <name> may contain whitespaces,
        while <id> must be a single token. Empty lines are ignored.

        The output is a list, each item is a tuple consisting of (<name>, <id>).

    """
    voters = []
    lineno = 1
    for line in text.split("\n"):
        line = line.strip()

        # ignore empty lines
        if not line:
            continue

        # extract (name, id)
        match = re.match(r'^(?P<name>.+)\s+(?P<id>[a-zA-Z0-9_\-]+)$', line)
        if not match:
            raise Exception(_("Incorrect format on line %(line)d: %(content)s")
                            % {'line': lineno, 'content': line})
        name = match.group('name').strip()
        id = match.group('id')
        voters.append((name, id))

        lineno += 1

    return voters

class AddVoterForm(forms.Form):
    voters_input = forms.CharField(label=_("Input"),
                                   widget=forms.Textarea)

    def clean_voters_input(self):
        data = self.cleaned_data['voters_input']
        try:
            self._voters = parse_voters(data)
        except Exception as e:
            raise forms.ValidationError(str(e))
        # don't allow empty input
        if not self._voters:
            raise forms.ValidationError(_("You must input at least 1 voter"))
        return data

    def save(self, voting_event):
        insert_list = []
        for (voter_name, voter_id) in self._voters:
            insert_list.append(Voter(event=voting_event,
                                     full_name=voter_name,
                                     username=voter_id))
        Voter.objects.bulk_create(insert_list)

    def get_voters(self):
        try:
            return self._voters
        except:
            return []

class AddVoterConfirmForm(forms.Form):

    def save(self):
        """ This form is just used as confirmation and saves nothing. """
        pass

class CheckInfoForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['username', 'passphrase']
        widgets = {'passphrase': forms.PasswordInput()}
