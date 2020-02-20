from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # ex: /playbooks_parser/5
    path('<int:playbook_id>', views.playbook, name='playbook'),
    # ex: /playbooks_parser/5/parsed/
    path('<int:playbook_id>/parsed/', views.playbook_parsed, name='playbook_parsed')
]
