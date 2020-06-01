from .models import Package, Playbook, PlaybookExecution, State, Task
from formal_iac import settings

from bs4 import BeautifulSoup
import requests
import yaml
from datetime import datetime


def parse_playbook_aux(playbook_content: str):
    list_of_tasks_dicts = yaml.load(playbook_content)[0]['tasks']
    return list_of_tasks_dicts


# INPUT: Playbook Content
# OUTPUT: List of the tasks it contains
def create_tasks(playbook_content: str):
    list_of_tasks = parse_playbook_aux(playbook_content)
    created_tasks = []
    for task in list_of_tasks:
        task_created = Task(task_name=task['name'] + " " + str(datetime.now()), task_module=list(task)[1],
                            module_arguments=task['yum']['name'], module_options=task['yum']['state'])
        task_created.save()
        created_tasks.append(task_created)
    return created_tasks


# Auxiliary function to create a playbook from an uploaded file
# Will be called only when a playbook is uploaded
def create_playbook(uploaded_content):
    playbook_content = ""
    for line in uploaded_content:
        playbook_content = playbook_content + line.decode("utf-8")
    list_of_tasks = create_tasks(playbook_content)
    playbook_created = Playbook(playbook_name="Uploaded_playbook " + str(datetime.now()),
                                playbook_content=playbook_content)
    playbook_created.save()
    playbook_created.list_of_tasks.set(list_of_tasks)
    playbook_created.save()
    return playbook_created


# Auxiliary function to create the states the execution of a playbook will generate
def create_playbook_execution(playbook_to_analyze):
    pl_name = playbook_to_analyze.playbook_name
    execution_created = PlaybookExecution(execution_id=pl_name + " analysis")
    execution_created.save()
    initial_state = State(state_name=pl_name + " initial state")
    initial_state.save()
    execution_created.list_of_states.add(initial_state)
    state_counter = 0
    # For each task in the playbook's list of tasks, create a state
    for task in playbook_to_analyze.list_of_tasks.all():
        state_counter += 1
        # The new state is the previous one with one more package
        if task.module_options == 'present':
            state_aux = State(state_name=pl_name + " state " + str(state_counter))
            state_aux.save()
            # TODO Try to fetch the package if it does not exists create it
            new_package = Package(package_name=task.module_arguments)
            new_package.save()
            # TODO Take the previous state and add those to the relation too
            state_aux.set_of_packages.add(new_package)
            execution_created.list_of_states.add(state_aux)


def create_dict_vuln_packages_aux():
    soup = BeautifulSoup(requests.get(settings.CANONICAL_PACKAGE_INFO_URL).text, "html.parser")
    table_of_packages = soup.find(id='cves').tbody.find_all('tr')
    dict_of_vulnerable_packages = {}
    # Dict structure
    # Entries where the package name is the key
    # The values is a list of tuples CVE's (including their href) + Impact
    for table_row in table_of_packages:
        if 'low' in table_row['class'] or 'high' in table_row['class']:
            package_name = table_row.find_all('td', class_='pkg')[0].a.text
            cve_name = table_row.find_all('td', class_='cve')[0].a.text
            cve_url = "https://nvd.nist.gov/vuln/detail/" + cve_name
            # cve_url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name=" + cve_name
            if package_name in dict_of_vulnerable_packages.keys():
                dict_of_vulnerable_packages[package_name].append(
                    (cve_name, cve_url, table_row['class'][0]))
            else:
                dict_of_vulnerable_packages[package_name] = [
                    (cve_name, cve_url, table_row['class'][0])]
    return dict_of_vulnerable_packages


# INPUT: a list of dictionaries specifying tasks on a playbook (in this case package installations)
# OUTPUT: a list of tuples where first element is the package name and the second element is the available CVEs
def analyse_vuln_packages(playbook):
    playbook_warnings = []
    # Construct source of vulnerable packages
    vuln_packages = create_dict_vuln_packages_aux()
    for task in playbook.list_of_tasks.all():
        package_name = task.module_arguments
        if package_name in vuln_packages.keys():
            playbook_warnings.append((package_name, vuln_packages[package_name]))
    return playbook_warnings


# Probably not useful but keep it just in case
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
