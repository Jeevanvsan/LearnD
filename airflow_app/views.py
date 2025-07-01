import importlib
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Course, tools_handson
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

@login_required
def get_user_handson(request,tool_id):
    user = request.user
    existing_tools_handson = tools_handson.objects.filter(user=user.id,tool_name = TOOL_NAME_MAIN[tool_id]).values().first()
    return JsonResponse(existing_tools_handson, safe=False)


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
def update_quiz(request,tool_id):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        course_id = data.get('course_id')
        score = data.get('score')
        existing_course_data = Course.objects.filter(user=user.id,course_id=course_id,tool_name=TOOL_NAME_MAIN[tool_id]).values()
        readable_courses = list([serialize_course(course,course_id,tool_id) for course in existing_course_data])[0]

        is_completed = readable_courses['quiz']
        if not is_completed:
            
            retries = readable_courses['quiz_retries']
            if score == 20:
                quiz = True
                status = "Completed"
                normalized_score = (score / 20) * 100
                penalty = 3 * retries
                final_score = round(max(0, normalized_score - penalty))
                Course.objects.filter(user=user.id,course_id=course_id,tool_name=TOOL_NAME_MAIN[tool_id]).update(quiz=quiz,score=final_score,status=status,end_time=timezone.now())

            else:
                Course.objects.filter(user=user.id,course_id=course_id,tool_name=TOOL_NAME_MAIN[tool_id]).update(quiz_retries=retries+1)

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

def hms_to_seconds(hms):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(hms.split(":"))))

def evaluate_dynamic_performance(time_taken_sec, min_time_str, max_time_str):
    min_time_sec = hms_to_seconds(min_time_str)
    max_time_sec = hms_to_seconds(max_time_str)

    if time_taken_sec <= min_time_sec:
        points = 100
    elif time_taken_sec >= max_time_sec:
        points = 25
    else:
        # Linear interpolation of points between min_time and max_time
        range_time = max_time_sec - min_time_sec
        time_diff = time_taken_sec - min_time_sec
        points = 100 - ((time_diff / range_time) * 75)
        points = round(points)

    # Determine stars
    if points >= 80:
        stars = 3
    elif points >= 50:
        stars = 2
    elif points >= 30:
        stars = 1
    else:
        stars = 0

    return {
        "points": points,
        "stars": stars
    }
    
def normalize_quotes(text):
    return text.replace('"', "'")

@csrf_exempt
def submit_code(request):
    global code_extr
    test_output = {}

    if request.method == 'POST':
        try:
            user = request.user
            task_metadata = {}
            handson_data = tools_handson.objects.filter(user=user.id).values().first()
            if handson_data is not None:
                task_metadata = handson_data.get('task_metadata', {})

            data = json.loads(request.body)
            code = data.get('code', '')
            tool_id = data.get('tool', '')
            time_taken = data.get('time', '')

            questions_data = get_problems_data(tool_id)
            problem = next((item for item in questions_data if item['id'] == question_id), None)

            if not problem:
                return JsonResponse({"response": "Error", "Error": "Invalid question ID"})
            module_name = f"airflow_app.executer.{tool_id}_executer"
            module = importlib.import_module(module_name)
            func = getattr(module, tool_id + "_executer")
            out = func(code)
            # Compare output
            sample_output = problem.get("sample_output", "").strip()
            output_matches = sample_output == out.strip()

            # Check keyword presence (optional)
            required_keywords = problem.get("keywords", [])
            code_normalized = normalize_quotes(code.lower())
            missing_keywords = []

            for keyword in required_keywords:
                keyword_normalized = normalize_quotes(keyword.lower())
                if keyword_normalized not in code_normalized:
                    missing_keywords.append(keyword)


            # Final decision
            error_message = out
            if missing_keywords:
                error_message += "\n\nMissing keywords: " + ", ".join(missing_keywords)

            test_output = {
                "response": "Correct" if output_matches and not missing_keywords else "Incorrect",
                "Error": error_message
            }
            

            result = evaluate_dynamic_performance(time_taken, problem.get("min_time"), problem.get("max_time"))
            status = ''
            if test_output["response"] == "Correct":   
                             
                existing_entry = task_metadata.get(str(question_id))  # Ensure key is a string
                should_update = False

                if not existing_entry:
                    should_update = True
                else:
                    existing_points = existing_entry.get("point", 0)
                    existing_time = existing_entry.get("time_taken", float('inf'))

                    if result["points"] > existing_points:
                        should_update = True
                    elif result["points"] == existing_points:
                        if time_taken < existing_time:
                            should_update = True

                if should_update:
                    task_metadata[str(question_id)] = {
                        "status": "Correct",
                        "time_taken": time_taken,
                        "point": result["points"],
                        "statrs": result["stars"]
                    }

                    tools_handson.objects.update_or_create(
                        user=user.id,
                        tool_name=TOOL_NAME_MAIN[tool_id],
                        defaults={
                            'tool_name': TOOL_NAME_MAIN[tool_id],
                            'status': status,
                            'task_metadata': task_metadata
                        }
                    )


            return JsonResponse({'output': test_output, 'code_extr': ""})
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


def python_study(request):
    return render(request, 'python_app/python-study.html')
