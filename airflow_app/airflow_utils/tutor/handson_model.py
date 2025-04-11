import json
import requests
import re
from django.conf import settings
import random

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
            You are a strict Python code evaluator.

            Respond only in this exact JSON format and nothing else:
            {{
            "response": "Correct" or "Incorrect",
            "Error": "Error message  or null"
            }}

            Rules:
            - Do not explain.
            - Do not include code.
            - Do not include code/samples/examples on Error.
            - Do not describe anything.
            - Only return the JSON.

            Evaluate the following:

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

    print("Payload: ", payload)

    response = requests.post(API_URL, json=payload, headers=HEADERS)

    if response.status_code == 200:
        result = response.json()
        print("Response: ", result)
        generated = result['choices'][0]['message']['content']
        print("Generated Response: ", generated)
        # Extract JSON only
        try:
            json_match = re.search(r'\{[\s\S]*?\}', generated)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                # print("Parsed JSON: ", parsed)
                return parsed
            else:
                return {"response": "Incorrect", "Error": "Invalid format returned"}
        except Exception as e:
            return {"response": "Incorrect", "Error": str(e)}

    else:
        print(f" Error {response.status_code}: {response.text}")
        return None


