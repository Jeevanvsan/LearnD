from django.urls import path
from django.conf.urls.static import static

from LearnD import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('run-code/', views.run_code, name='run_code'),
    path('submit-code/', views.submit_code, name='submit_code'),
    path('airflow-do/<int:problem_id>/', views.airflow_do, name='airflow_do'),
    path('airflow-study/', views.airflow_study, name='airflow_study'),
]



