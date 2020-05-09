
from django.http import JsonResponse

# views.py
from django.db import connections
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .models import Task, Playbook, State, Package
from .forms import ParsePlaybookDemoForm
from graphviz import Digraph
import yaml


# First way of returning a rendered template
# TO-DO Modify to display design 1
def index_view(request):
    latest_uploaded_playbooks = Playbook.objects.order_by('playbook_name')[:2]
    template = loader.get_template("playbooks_parser/index.html")
    context = {
        'latest_uploaded_playbooks': latest_uploaded_playbooks,
    }
    return HttpResponse(template.render(context, request))


def playbook_view(request, playbook_id):
    requested_playbook = get_object_or_404(Playbook, pk=playbook_id)
    context = {
        'requested_ṕlaybook': requested_playbook,
    }
    return render(request, 'playbooks_parser/playbook.html', {'requested_playbook' : requested_playbook})


def playbook_parsed_view(request, playbook_id):
    requested_playbook = get_object_or_404(Playbook, pk=playbook_id)
    parsed_playbook = yaml.load(requested_playbook.playbook_content)
    context = {
        'parsed_playbook': parsed_playbook,
    }
    return render(request, 'playbooks_parser/parsed_playbook.html', {'parsed_playbook': parsed_playbook})


# Quickest way to return a rendered template
def state_view(request):
    latest_states_list = State.objects.order_by('state_name')[:5]
    context = {
        'states_list': latest_states_list,
    }
    return render(request, "playbooks_parser/state.html", context)


def demo_view(request):
    form = ParsePlaybookDemoForm()
    context = {
        'form': form
    }
    return render(request, 'playbooks_parser/demo.html', context)


# Auxiliary function to create a playbook from an uploaded file
def create_playbook(f):
    playbook_content = ""
    for line in f:
        playbook_content = playbook_content + line.decode("utf-8")
    return Playbook.create("Uploaded_playbook", playbook_content)


def demo_result_view(request):
    if request.method == 'POST':
        # Retrieve posted information
        form = ParsePlaybookDemoForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['playbook_examples'] != '0':
                playbook_requested_to_parse = Playbook.objects.get(pk=form.cleaned_data['playbook_examples'])
            else:
                playbook_requested_to_parse = create_playbook(form.cleaned_data['uploaded_playbook'])
            list_of_tasks = parse_playbook_aux(playbook_requested_to_parse.playbook_content)
            context = {
                'parsed_playbook': str(list_of_tasks),
                'playbook_tasks': list_of_tasks
            }
            return render(request, "playbooks_parser/demo_result.html", context)
    return {}

# Quick PoC
def graph_view(request):
    dot = Digraph(comment='plotted state')
    dot.node('A', '[yum_a, ansible_b]')
    dot.node('B', '[test_1, test_2]')
    dot.edge('A', 'B', 'add test_1')
    dot.format = 'svg'
    context = {
        'rendered_state': dot.pipe().decode('utf-8')
    }
    # Algorithm:
    # You request the run of a playbook on /playbooks_parser/<playbook_id>/run
    # Get list of vulnerable packages
    # Get initial state and add it as a node
    # For every action define a transition and register that state
    # If you are adding/updating a package check the package with the list
    # Color it if its on it with red or orange, or green if not

    return render(request, 'playbooks_parser/graph.html', context)


# TO-DO Parsing Logic
# TO-DO change type hint to list of tasks
# Return a list of Tokens
def parse_playbook_aux(playbook_content: str):
    list_of_tasks = yaml.load(playbook_content)[0]['tasks']
    return list_of_tasks
    # TO-DO: Create a token for each identified task, maybe even instead a task?


def install_package_aux(playbook_id, package_name, package_version):
    Playbook.objects.filter(pk=playbook_id)
    installed_package = Package(package_name=package_name, package_version=package_version)
    installed_package.save()
    state_to_install = State.objects.all()['current_state']
    state_to_install.set_of_packages.add(installed_package)


def update_package_aux(playbook_id, package_name, package_version, state_to_install):
    Playbook.objects.filter(pk=playbook_id)
    installed_package = Package(package_name=package_name, package_version=package_version)
    installed_package.save()
    state_to_install.set_of_packages.add(installed_package)


def delete_package_aux(playbook_id, package_name, package_version):
    Playbook.objects.filter(pk=playbook_id)
    installed_package = Package(package_name=package_name, package_version=package_version)
    installed_package.save()
    state_to_install = State.objects.all()['current_state']
    state_to_install.set_of_packages.add(installed_package)


def get_current_state_aux():
    return State.objects.filter(current_state=True)