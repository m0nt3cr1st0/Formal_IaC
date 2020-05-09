from django import forms

EXAMPLE_PLAYBOOKS = [('1', 'Install python and wget'), ('2', 'Install httpd and nginx')]


class ParsePlaybookDemoForm(forms.Form):
    playbook_examples = forms.ChoiceField(label='Parse a playbook example', widget=forms.RadioSelect,
                                          choices=EXAMPLE_PLAYBOOKS)
    uploaded_playbook = forms.FileField(label='Upload your own playbook', required=False)

