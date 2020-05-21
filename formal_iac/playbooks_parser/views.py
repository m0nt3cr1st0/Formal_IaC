
from django.http import JsonResponse

# views.py
from django.db import connections
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .forms import ParsePlaybookDemoForm
from .models import Task, Playbook, State, Package
from formal_iac import settings

from bs4 import BeautifulSoup
from graphviz import Digraph
import requests
import yaml


def parse_playbook_aux(playbook_content: str, vuln_packages):
    playbook_tasks = yaml.load(playbook_content)[0]['tasks']
    playbook_warnings = []
    for task in playbook_tasks:
        task_command = task.keys()[1]
        package_name = task[task_command]['name']
        package_operation = task[task_command]['state']
        if vuln_packages['package_name']:
            playbook_warnings.append(vuln_packages['package_name'])
    return playbook_warnings


def create_dict_vuln_packages_aux():
    soup = BeautifulSoup(requests.get(settings.CANONICAL_PACKAGE_INFO_URL).text, "html.parser")
    # print(soup.find(id='cves').tbody)
    table_of_packages = soup.find(id='cves').tbody.find_all('tr')
    dict_of_vulnerable_packages = {}
    # Dict structure
    # Entries where the package name is the key
    # The values is a list of tuples CVE's (including their href) + Impact
    for table_row in table_of_packages:
        if 'low' in table_row['class'] or 'high' in table_row['class']:
            package_name = table_row.find_all('td', class_='pkg')[0].a.text
            if package_name in dict_of_vulnerable_packages.keys():
                dict_of_vulnerable_packages[package_name].append(
                    (table_row.find_all('td', class_='cve')[0], table_row['class'][0]))
            else:
                dict_of_vulnerable_packages[package_name] = [
                    (table_row.find_all('td', class_='cve')[0], table_row['class'][0])]
    return dict_of_vulnerable_packages


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
        # Construct source of vulnerable packages
        dict_of_vulnerable_packages = create_dict_vuln_packages_aux()
        # Retrieve posted information
        form = ParsePlaybookDemoForm(request.POST, request.FILES)
        if form.is_valid():
            # Form validation, retrieve the playbook to analyze
            if form.cleaned_data['playbook_examples'] == '0' and form.cleaned_data['uploaded_playbook'] is not None:
                playbook_requested_to_parse = create_playbook(form.cleaned_data['uploaded_playbook'])
                playbook_content = playbook_requested_to_parse.playbook_content
            elif form.cleaned_data['playbook_examples'] != '0':
                playbook_requested_to_parse = Playbook.objects.get(pk=form.cleaned_data['playbook_examples'])
                playbook_content = playbook_requested_to_parse.playbook_content
            else:
                playbook_content = ""

            # With the playbook retrieved access its content and analyze the packages to be installed
            if playbook_content != "":
                list_of_tasks = parse_playbook_aux(playbook_content)
            #
            else:
                list_of_tasks = []
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

