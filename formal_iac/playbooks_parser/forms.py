from django import forms

EXAMPLE_PLAYBOOKS = [('1', 'Install 1'), ('2', "Install 2")]


class ParsePlaybookDemoForm(forms.Form):
    playbook_examples = forms.ChoiceField(widget=forms.RadioSelect, choices=EXAMPLE_PLAYBOOKS)

