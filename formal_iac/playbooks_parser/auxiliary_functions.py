from .models import Task, Playbook, State, Package
from formal_iac import settings

from bs4 import BeautifulSoup
import requests
import yaml


def parse_playbook_aux(playbook_content: str):
    playbook_tasks = yaml.load(playbook_content)[0]['tasks']
    return playbook_tasks


def analyse_vuln_packages_aux(playbook_tasks, vuln_packages):
    playbook_warnings = []
    for task in playbook_tasks:
        # TO-DO: make it expandable to other ansible modules
        task_command = 'yum'
        package_name = task[task_command]['name']
        package_operation = task[task_command]['state']
        if package_name in vuln_packages.keys():
            playbook_warnings.append((package_name, vuln_packages[package_name]))
    return playbook_warnings


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
            #cve_url = "https://nvd.nist.gov/vuln/detail/" + cve_name
            cve_url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name=" + cve_name
            if package_name in dict_of_vulnerable_packages.keys():
                dict_of_vulnerable_packages[package_name].append(
                    (cve_name, cve_url, table_row['class'][0]))
            else:
                dict_of_vulnerable_packages[package_name] = [
                    (cve_name, cve_url, table_row['class'][0])]
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

# INPUT: Playbook Content
# OUTPUT: List of the tasks it contains
def create_tasks(playbook_content:str):
    list_of_tasks = parse_playbook_aux(playbook_content)
    created_tasks=[]
    for task in list_of_tasks:
        task_created = Task(task_name=task['name'], task_module=list(task)[1], task_arguments=task['yum']['name'],
                            task_options=task['yum']['state'])
        task_created.save()
        created_tasks.append(task_created)
    return task_created


# Auxiliary function to create a playbook from an uploaded file
def create_playbook(uploaded_content):
    playbook_content = ""
    for line in uploaded_content:
        playbook_content = playbook_content + line.decode("utf-8")
    list_of_tasks = create_tasks(playbook_content)
    return Playbook(playbook_name="Uploaded_playbook", playbook_content=playbook_content, list_of_tasks=list_of_tasks)


# Auxiliary function to create the states the execution of a playbook will generate
def create_playbook_execution(playbook_to_analyze):
    initial_state = State(state_name=playbook_to_analyze.playbook_name + " initial state")
    # For each task in the playbook's list of tasks, create a package and a state
    for task in playbook_to_analyze.list_of_tasks:
        if task.module_options == 'present':
            # TODO: create method that given a package tells you last version
            package_to_install = Package(package_name=task.module_arguments,
                                         package_version))

