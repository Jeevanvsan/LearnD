import requests
import re
from django.conf import settings

OPENROUTER_API_KEY = settings.ROUTE_KEY  

MODEL = "meta-llama/llama-4-maverick:free" 

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://yourdomain.com",  # Optional: your app or GitHub link
    "X-Title": "code-evaluator"
}

API_URL = "https://openrouter.ai/api/v1/chat/completions"

def check_ans(qn, ans):
    prompt = f"""
            You are a strict and concise Python code evaluator.

            Only respond in this exact JSON format and nothing else:
            {{
            "response": "Correct" or "Incorrect",
            "Error": "Only mention the exact error if any. If no error, return None."
            }}

            Make sure:
            - Do not explain the code.
            - Do not describe what it does.
            - Do not include any output or interpretation.
            - Check DAG code syntax and mandatory imports,fields.

            Question:
            {qn}

            Answer:
            {ans}
            """

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a strict code evaluator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }

    response = requests.post(API_URL, json=payload, headers=HEADERS)

    if response.status_code == 200:
        result = response.json()
        generated = result['choices'][0]['message']['content']

        match = re.search(r'\b(Correct|Incorrect)\b', generated, re.IGNORECASE)
        if match:
            decision = match.group(1).capitalize()
            return generated
        else:
            return "Unknown"

    else:
        print(f" Error {response.status_code}: {response.text}")
        return None


