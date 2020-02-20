from django.db import models


class Package(models.Model):
    package_name = models.CharField(max_length=200)
    package_version = models.FloatField

    def __str__(self):
        return self.package_name


class State(models.Model):
    set_of_packages = models.ManyToManyField(Package)


class Task(models.model):
    task_name = models.CharField(max_length=200)
    task_module = models.CharField(max_length=200)
    # module_arguments should be a list of strings for each option
    module_options = models.CharField(max_length=200)
    # module_arguments should be a list of strings for each argument
    module_arguments = models.CharField(max_length=200)


class Playbook(models.model):
    list_of_tasks = models.ManyToManyField(Task)

