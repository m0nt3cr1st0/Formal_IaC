from django.urls import path

from . import views

app_name = 'playbooks_parser'
urlpatterns = [
    # ex: /playbooks_parser/
    path('', views.index_view, name='index_view'),
    # ex: /playbooks_parser/5
    path('<int:playbook_id>', views.playbook_view, name='playbook_view'),
    # ex: /playbooks_parser/5/parsed/
    path('<int:playbook_id>/parsed/', views.playbook_parsed_view, name='playbook_parsed_view'),
    # ex: /select_analysis
    path('select_analysis', views.select_analysis_view, name='select_analysis_view'),
    # ex: /demo
    path('demo', views.demo_view, name='demo_view'),
    # ex: /demo_result_view
    path('demo_result', views.demo_result_view, name='demo_result_view')
]

