from django import forms

AVAILABLE_ANALYSES = [('0', 'Vulnerability Analysis')]


class SelectAnalysisForm(forms.Form):
    available_analyses = forms.ChoiceField(label='Select an analysis to apply', widget=forms.RadioSelect,
                                           choices=AVAILABLE_ANALYSES, required=True)


EXAMPLE_PLAYBOOKS = [('0', 'Upload your own playbook'),
                     ('1', 'Install python and wget'),
                     ('2', 'Install httpd and nginx')]


class ParsePlaybookDemoForm(forms.Form):
    playbook_examples = forms.ChoiceField(label='Parse a playbook example', widget=forms.RadioSelect,
                                          choices=EXAMPLE_PLAYBOOKS, required=True)
    uploaded_playbook = forms.FileField(label='Upload your own playbook', required=False)
