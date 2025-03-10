from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import io
import contextlib

from airflow_app.airflow_utils.airflow_code_extractor import DagExtract



def index(request):
    return render(request, 'airflow_app/index.html')

@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            code = data.get('code', '')
            ob = DagExtract()
            result = ob.run(code)
            return JsonResponse({'output': result})
        except Exception as e:
            print(e)
            return JsonResponse({'output': str(e)})

    return JsonResponse({'output': 'Invalid request'})
