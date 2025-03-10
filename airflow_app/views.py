from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import io
import contextlib



def index(request):
    return render(request, 'airflow_app/index.html')

@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            code = data.get('code', '')
            print(code)
            # Capture the output of the code execution
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(code, {'__name__': '__main__'})
            result = output.getvalue()

            print(output.getvalue())

            return JsonResponse({'output': result})
        except Exception as e:
            return JsonResponse({'output': str(e)})

    return JsonResponse({'output': 'Invalid request'})
