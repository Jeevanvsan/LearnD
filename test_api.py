import requests

resp = requests.post(
    "http://35.222.183.36:5000/run",
    json={"code": "a=2\nb=3\nprint('sum =', a+b)", "input": ""}
)
print(resp.json())
