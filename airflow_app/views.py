import importlib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Course
from django.core.serializers import serialize
from django.utils import timezone

from airflow_app.airflow_utils.airflow_code_extractor import DagExtract
from airflow_app.airflow_utils.tutor import handson_model 

question_id = 0
code_extr = None

# TOOL_NAME = 'Apache Airflow'
TOOL_NAME_MAIN = {"AF": "Apache Airflow", "PY": "Python"}



# py manage.py runserver
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\lenv\Scripts\Activate.ps1


with open('airflow_app/static/airflow_app/json_data/airflow_courses.json', 'r') as file:
    airflow_courses_data = json.load(file)
    
def get_courses_data(tool_name):
    if tool_name == 'AF':
        with open('airflow_app/static/airflow_app/json_data/airflow_courses.json', 'r') as file:
            return json.load(file)
    if tool_name == 'PY':
        with open('airflow_app/static/python_app/json_data/python_courses.json', 'r') as file:
            return json.load(file)
        
def get_tut_data(id,tool_req):
    if tool_req == 'AF':
        with open(f'airflow_app/static/airflow_app/json_data/{id}.json', 'r') as file:
            return json.load(file)
    if tool_req == 'PY':
        with open(f'airflow_app/static/python_app/json_data/{id}.json', 'r') as file:
            return json.load(file)
        
def get_problems_data(tool_req):
    if tool_req == 'AF':
        with open(f'airflow_app/static/airflow_app/json_data/problems.json', 'r') as file:
            return json.load(file)
    if tool_req == 'PY':
        with open(f'airflow_app/static/python_app/json_data/problems.json', 'r') as file:
            return json.load(file)

@login_required
def index(request):
    if request.user.is_authenticated:
        user = request.user
        return render(request, 'index.html',{'user': user})
    else:
        return redirect('signin')
    
@login_required
def airflow_index(request):
    if request.user.is_authenticated:
        user = request.user
        return render(request, 'airflow_app/airflow-main.html',{'user': user})
    else:
        return redirect('signin')

@login_required
def get_user_courses(request):
    user = request.user
    existing_courses = Course.objects.filter(user=user.id).values_list('course_id',flat=True)
    existing_courses_json = json.dumps(list(existing_courses))
    return JsonResponse(existing_courses_json, safe=False)


def serialize_course(course,id,tool_req):
    tut_data = get_tut_data(id,tool_req)
    return {
        **course,
        'total_chapters': len(tut_data),
        'start_time': course['start_time'].strftime('%Y-%m-%d %H:%M:%S') if course['start_time'] else None,
        'updated_time': course['updated_time'].strftime('%Y-%m-%d %H:%M:%S') if course['updated_time'] else None,
        'end_time': course['end_time'].strftime('%Y-%m-%d %H:%M:%S') if course['end_time'] else None,
    }

@csrf_exempt
@login_required
def get_courses(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        course_id = data.get('course_id')
        tool_req = data.get('tool')
        existing_course = Course.objects.filter(user=user.id,course_id=course_id,tool_name=TOOL_NAME_MAIN[tool_req]).values()
        readable_courses = [serialize_course(course,course_id,tool_req) for course in existing_course]
    
    return JsonResponse(list(readable_courses), safe=False)

def airflow_study(request):
    return render(request, 'airflow_app/airflow-study.html')

@csrf_exempt
@login_required
def update_progress(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        course_id = data.get('course_id')        
        tool_req = data.get('tool')  
        course_data = get_courses_data(tool_req) 
        course_name = course_data.get(course_id).get('title')
        status = 'In Progress'
        chapter = data.get('chapter') 
        Course.objects.update_or_create(user=user.id,course_id=course_id,
                    defaults={
                    'tool_name': TOOL_NAME_MAIN[tool_req],
                    'course_name': course_name,
                    'status': status,
                    'chapters': chapter                             
            })
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def calculate_final_score(quiz_score, retries, max_quiz_score=20):
    normalized_score = (quiz_score / max_quiz_score) * 100
    penalty = 3 * retries
    final_score = max(0, normalized_score - penalty)
    return round(final_score, 2)


@csrf_exempt
@login_required
def update_quiz(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        course_id = data.get('course_id')
        score = data.get('score')
        existing_course_data = Course.objects.filter(user=user.id,course_id=course_id,tool_name=TOOL_NAME).values()
        readable_courses = list([serialize_course(course,course_id) for course in existing_course_data])[0]

        is_completed = readable_courses['quiz']
        if not is_completed:
            
            retries = readable_courses['quiz_retries']
            if score == 20:
                quiz = True
                status = "Completed"
                normalized_score = (score / 20) * 100
                penalty = 3 * retries
                final_score = round(max(0, normalized_score - penalty))
                Course.objects.filter(user=user.id,course_id=course_id,tool_name=TOOL_NAME).update(quiz=quiz,score=final_score,status=status,end_time=timezone.now())

            else:
                Course.objects.filter(user=user.id,course_id=course_id,tool_name=TOOL_NAME).update(quiz_retries=retries+1)

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def airflow_do(request,tool_id,problem_id):
    global question_id
    question_id = problem_id
    questions_data = get_problems_data(tool_id)
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
            tool_id = data.get('tool', '')
            module_name = f"airflow_app.executer.{tool_id}_executer"  
            module = importlib.import_module(module_name)
            func = getattr(module, tool_id + "_executer")
            out = func(code)
            return JsonResponse({'output': out})
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
            tool_id = data.get('tool', '')
            questions_data = get_problems_data(tool_id)
            problem = next((item for item in questions_data if item['id'] == question_id), None)
            module_name = f"airflow_app.executer.{tool_id}_executer"  
            module = importlib.import_module(module_name)
            func = getattr(module, tool_id + "_executer")
            out = func(code)
            #TODO: Add code extraction logic
            # if code_extr is None:
            # test_output = handson_model.check_ans(problem["question"],code)
            test_output = {"response": "Correct", "Error": "Incorrect answer, try again or check your code. "}
            return JsonResponse({'output': out, 'code_extr': ""})
        except Exception as e:
            print(e)
            return JsonResponse({'output': str(e)})


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        else:
            user = User(
                username=username,
                email=email,
                last_login=timezone.now(),  # Set before saving
                is_active=True
            )
            user.set_password(password)  # Hash the password
            user.save()

            Profile.objects.create(user=user, user_id=user.id)
            messages.success(request, 'Account created successfully')
            return redirect('signin')

    return render(request, 'signup.html')


def signin_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        user.last_login = timezone.now()  
        user.save()
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'signin.html')


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        user = request.user
        performance_score = Profile.objects.get(user=user).score
        certificates = Profile.objects.get(user=user).certificates
        return render(request, 'index.html', {'user': user})
    else:
        return redirect('signin')

def logout_view(request):
    logout(request)
    return redirect('signin')


# Python 

with open('airflow_app/static/python_app/json_data/problems.json', 'r') as file:
    python_questions_data = json.load(file)

with open('airflow_app/static/python_app/json_data/python_courses.json', 'r') as file:
    python_courses_data = json.load(file)

@login_required
def python_index(request):
    if request.user.is_authenticated:
        user = request.user
        return render(request, 'python_app/python-main.html',{'user': user})
    else:
        return redirect('signin')

def python_do(request, tool_id, problem_id):
    global question_id
    question_id = problem_id
    questions_data = get_problems_data(tool_id)
    problem = next((item for item in questions_data if item['id'] == problem_id), None)
    return render(request, 'python_app/python-do.html',{'problem': problem})



    return JsonResponse({'output': 'Invalid request'})

def python_study(request):
    return render(request, 'python_app/python-study.html')
