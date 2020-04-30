from django.db import models


class Package(models.Model):
    package_name = models.CharField(max_length=200)
    package_version = models.FloatField()

    def __str__(self):
        return self.package_name + " " + str(self.package_version)


class State(models.Model):
    state_name = models.CharField(max_length=200)
    set_of_packages = models.ManyToManyField(Package)


class Task(models.Model):
    task_name = models.CharField(max_length=200)
    task_module = models.CharField(max_length=200)
    # module_arguments should be a list of strings for each option
    module_options = models.CharField(max_length=200)
    # module_arguments should be a list of strings for each argument
    module_arguments = models.CharField(max_length=200)

    def __str__(self):
        return self.task_name


class Playbook(models.Model):
    playbook_name = models.CharField(max_length=200)
    # Text Field instead of Charfield as it is potentially a huge amount of characters
    playbook_content = models.TextField()
    list_of_tasks = models.ManyToManyField(Task)

    def __str__(self):
        return self.playbook_name
