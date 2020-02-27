from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Task, Playbook, State

import yaml


# First way of returning a rendered template
def index(request):
    latest_uploaded_playbooks = Playbook.objects.order_by('id')[:5]
    template = loader.get_template("playbooks_parser/index.html")
    context = {
        latest_uploaded_playbooks: latest_uploaded_playbooks,
    }
    return HttpResponse(template.render(context, request))


def playbook(request, playbook_id):
    requested_playbook = get_object_or_404(Playbook, pk=playbook_id)
    context = {
        'requested_ṕlaybook': requested_playbook
    }
    return render(request, 'playbooks/playbook.html', context)



