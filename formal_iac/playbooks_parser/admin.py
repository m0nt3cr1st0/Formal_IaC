
from django.contrib import admin

from .models import State, Package, Task, Playbook

admin.site.register(Package)
admin.site.register(State)
admin.site.register(Task)
admin.site.register(Playbook)
