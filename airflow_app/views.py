from django.shortcuts import render

def index(request):
    return render(request, 'airflow_app/index.html')
