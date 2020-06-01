
from django.contrib import admin

from .models import Package, Playbook, PlaybookExecution, State, Task, Vulnerability

admin.site.register(Package)
admin.site.register(Playbook)
admin.site.register(PlaybookExecution)
admin.site.register(State)
admin.site.register(Task)
admin.site.register(Vulnerability)
