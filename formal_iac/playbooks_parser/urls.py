from django.urls import path

from . import views

app_name = 'playbooks_parser'
urlpatterns = [
    # ex: /playbooks_parser/
    path('', views.index, name='index'),
    # ex: /playbooks_parser/5
    path('<int:playbook_id>', views.playbook, name='playbook'),
    # ex: /playbooks_parser/5/parsed/
    path('<int:playbook_id>/parsed/', views.playbook_parsed, name='playbook_parsed'),
    # ex: /playbooks_parser/states
    path('states', views.state, name='state')
]
