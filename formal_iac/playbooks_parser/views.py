from django.http import HttpResponse
from django.template import loader

from .models import Task, Playbook

import yaml


def index(request):
    template = loader.get_template("playbooks_parser/index.html")
    return HttpResponse(template.render())


def playbook(request):
    first_playbook = Playbook.objects.order_by('playbook_name')[0]
    output = first_playbook.playbook_name
    return HttpResponse(output)


def playbook_parsed(request, playbook_id):
    first_playbook = Playbook.objects.order_by('playbook_name')[0]
    output = first_playbook.playbook_name
    return HttpResponse("You're looking at playbook %s parsed" % playbook_id)

