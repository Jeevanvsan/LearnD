from django.urls import path
from django.conf.urls.static import static

from LearnD import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    
    ### Airflow related URLs
    path('airflow/', views.airflow_index, name='airflow_index'),
    path('run-code/', views.run_code, name='run_code'),
    path('submit-code/', views.submit_code, name='submit_code'),
    path('airflow-do/<int:problem_id>/', views.airflow_do, name='airflow_do'),
    path('airflow-study/', views.airflow_study, name='airflow_study'),
    path('get-user-courses/', views.get_user_courses, name='get_user_courses'),
    path('get-courses/', views.get_courses, name='get_courses'),
    path('update-progress/', views.update_progress, name='update_progress'),
    path('update-quiz/', views.update_quiz, name='update_progress'),
    
    ## Python related URLs
    path('python/', views.python_index, name='python_index'),
    path('run-code/', views.run_code, name='run_code'),
    path('submit-code/', views.submit_code, name='submit_code'),
    path('python-do/<str:tool_id>/<int:problem_id>/', views.python_do, name='python_do'),
    path('python-study/', views.python_study, name='python_study'),
    path('get-user-courses/', views.get_user_courses, name='get_user_courses'),
    path('get-user-handson/<str:tool_id>', views.get_user_handson, name='get_user_handson'),
    path('get-courses/', views.get_courses, name='get_courses'),
    path('update-progress/', views.update_progress, name='update_progress'),
    path('update-quiz/<str:tool_id>', views.update_quiz, name='update_progress'),


    
  
]



