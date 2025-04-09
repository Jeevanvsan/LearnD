from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import io
import contextlib

from airflow_app.airflow_utils.airflow_code_extractor import DagExtract
from airflow_app.airflow_utils.tutor import handson_model 

question_id = 0
code_extr = None

# py manage.py runserver

with open('airflow_app/static/airflow_app/problems.json', 'r') as file:
    questions_data = json.load(file)

def index(request):
    return render(request, 'airflow_app/airflow-main.html')

def airflow_study(request):
    return render(request, 'airflow_app/airflow-study.html')

def airflow_do(request,problem_id):
    global question_id
    question_id = problem_id
    problem = next((item for item in questions_data if item['id'] == problem_id), None)
    return render(request, 'airflow_app/airflow-do.html',{'problem': problem})

@csrf_exempt
def run_code(request):
    global code_extr
    global question_id

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            code = data.get('code', '')
            ob = DagExtract()
            code_extr = ob.run(code)
            return JsonResponse({'output': code_extr})
        except Exception as e:
            print(e)
            return JsonResponse({'output': str(e)})

    return JsonResponse({'output': 'Invalid request'})

@csrf_exempt
def submit_code(request):
    global code_extr
    ob = DagExtract()

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            problem = next((item for item in questions_data if item['id'] == question_id), None)
            # print(problem,"----")

            if code_extr is None:
                code_extr = ob.run(code)
            print(problem["question"])
            print(handson_model.check_ans(problem["question"],code))
            # ans_extr = ob.run(problem["answers"][0]["code"])
            # print("submitted code : ",code_extr)
            # print("Ans code : ",ans_extr)
            return JsonResponse({'output': code_extr})
        except Exception as e:
            print(e)
            return JsonResponse({'output': str(e)})

    return JsonResponse({'output': 'Invalid request'})

