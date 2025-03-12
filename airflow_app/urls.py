from django.urls import path
from django.conf.urls.static import static

from LearnD import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('run_code/', views.run_code, name='run_code'),
    path('airflow-do/', views.airflow_do, name='airflow_do'),
    path('airflow-study/', views.airflow_study, name='airflow_study'),
]



