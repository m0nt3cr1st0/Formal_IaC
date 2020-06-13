# views.py
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect

from .auxiliary_functions import create_playbook, create_playbook_execution
from .forms import ParsePlaybookDemoForm, SelectAnalysisForm
from .models import Playbook

from graphviz import Digraph
import yaml


def index_view(request):
    template = loader.get_template("playbooks_parser/index.html")
    return HttpResponse(template.render({}, request))


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


def select_analysis_view(request):
    if request.method == 'POST':
        return redirect('/demo')
    else:
        form = SelectAnalysisForm()
        context = {
            'form': form
        }
        return render(request, 'playbooks_parser/select_analysis.html', context)


def demo_view(request):
    form = ParsePlaybookDemoForm()
    context = {
        'form': form
    }
    return render(request, 'playbooks_parser/demo.html', context)


def demo_result_view(request):
    if request.method == 'POST':
        # Retrieve posted information
        form = ParsePlaybookDemoForm(request.POST, request.FILES)
        if form.is_valid():
            # Form validation, create/retrieve the playbook to analyze
            if form.cleaned_data['playbook_examples'] == '0' and form.cleaned_data['uploaded_playbook'] is not None:
                playbook_to_analyze = create_playbook(form.cleaned_data['uploaded_playbook'])
            elif form.cleaned_data['playbook_examples'] != '0':
                playbook_to_analyze = Playbook.objects.get(pk=form.cleaned_data['playbook_examples'])
            else:
                playbook_to_analyze = ""

            # Begin the analysis
            # With the playbook created/retrieved access its content and analyze the packages to be installed
            if playbook_to_analyze != "":
                playbook_execution = create_playbook_execution(playbook_to_analyze)
                list_of_tasks = playbook_to_analyze.list_of_tasks
            else:
                list_of_tasks = []
            context = {
                'playbook_tasks': list_of_tasks,
                'playbook_execution': playbook_execution
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

