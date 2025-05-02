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

TOOL_NAME = 'Apache Airflow'

# py manage.py runserver

with open('airflow_app/static/airflow_app/json_data/problems.json', 'r') as file:
    questions_data = json.load(file)

with open('airflow_app/static/airflow_app/json_data/airflow_courses.json', 'r') as file:
    courses_data = json.load(file)

@login_required
def index(request):
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


def serialize_course(course,id):
    with open(f'airflow_app/static/airflow_app/json_data/{id}.json', 'r') as file:
        courses_data = json.load(file)
    return {
        **course,
        'total_chapters': len(courses_data),
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
        existing_course = Course.objects.filter(user=user.id,course_id=course_id,tool_name=TOOL_NAME).values()
        readable_courses = [serialize_course(course,course_id) for course in existing_course]
    
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
        course_name = courses_data.get(course_id).get('title')
        status = 'In Progress'
        chapter = data.get('chapter') 
        Course.objects.update_or_create(user=user.id,course_id=course_id,
                    defaults={
                    'tool_name': TOOL_NAME,
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
            # if code_extr is None:
            code_extr = ob.run(code)
            print(problem["question"])
            # test_output = handson_model.check_ans(problem["question"],code)
            test_output = {"response": "Correct", "Error": "Incorrect answer, try again or check your code. "}
            print(test_output)
            return JsonResponse({'output': test_output, 'code_extr': code_extr})
        except Exception as e:
            print(e)
            return JsonResponse({'output': str(e)})

    return JsonResponse({'output': 'Invalid request'})

# def signup_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         if User.objects.filter(username=username).exists():
#             messages.error(request, 'Username already taken')
#         else:
#             user = User.objects.create_user(username=username, email=email, password=password)
#             user.last_login = timezone.now()  
#             user.save()
#             messages.success(request, 'Account created successfully')
#             Profile.objects.create(user=user,user_id = user.id)

#             return redirect('signin')
#     return render(request, 'signup.html')


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
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'signin.html')


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        user = request.user
        print(user.username)
        print(user.email)
        print(user.id)
        performance_score = Profile.objects.get(user=user).score
        certificates = Profile.objects.get(user=user).certificates
        print(performance_score,certificates)


        return render(request, 'dashboard.html', {'user': user})
    else:
        return redirect('signin')

def logout_view(request):
    logout(request)
    return redirect('signin')

