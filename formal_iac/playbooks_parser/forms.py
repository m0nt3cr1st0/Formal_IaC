from django import forms

EXAMPLE_PLAYBOOKS = [('1', 'Install 1'), ('2', 'Install 2'), ('0', 'Upload your own playbook')]


class ParsePlaybookDemoForm(forms.Form):
    playbook_examples = forms.ChoiceField(widget=forms.RadioSelect, choices=EXAMPLE_PLAYBOOKS)
    uploaded_playbook = forms.FileField()

