from django.db import models


class Package(models.Model):
    package_name = models.CharField(max_length=200)
    package_version = models.FloatField


# Create your models here.
class State(models.Model):
    set_of_packages = models.ManyToManyField(Package)



