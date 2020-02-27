from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Task, Playbook, State

import yaml


# First way of returning a rendered template
def index(request):
    latest_uploaded_playbooks = Playbook.objects.order_by('playbook_name')[:2]
    template = loader.get_template("playbooks_parser/index.html")
    context = {
        'latest_uploaded_playbooks': latest_uploaded_playbooks,
    }
    return HttpResponse(template.render(context, request))


def playbook(request, playbook_id):
    requested_playbook = get_object_or_404(Playbook, pk=playbook_id)
    context = {
        'requested_ṕlaybook': requested_playbook,
    }
    return render(request, 'playbooks_parser/playbook.html', {'requested_playbook' : requested_playbook})


def playbook_parsed(request, playbook_id):
    requested_playbook = get_object_or_404(Playbook, pk=playbook_id)
    parsed_playbook = yaml.load(requested_playbook.playbook_content)
    context = {
        'parsed_playbook': parsed_playbook,
    }
    return render(request, 'playbooks_parser/parsed_playbook.html', {'parsed_playbook': parsed_playbook})


# Quickest way to return a rendered template
def state(request):
    latest_states_list = State.objects.order_by('state_name')[:5]
    context = {
        'states_list': latest_states_list,
    }
    return render(request, "playbooks_parser/state.html", context)
