import base64
import requests
import json
import requests
import subprocess
import logging
import os


# URL for google recoginize
request_url = "https://vision.googleapis.com/v1/images:annotate"
jpg = os.path.join(os.path.dirname(__file__), 'images/7.9.jpg')
f = open(jpg, 'rb')
img = base64.b64encode(f.read())

print("starting")

data = {"requests": [{"image": {"content": img.decode("utf-8")}, "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]}]}
data_json = json.dumps(data)

request_url = request_url

token_file = os.path.join(os.path.dirname(__file__), 'token.file')

with open(token_file, 'r') as file:
    token = file.read().strip()

headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'x-goog-user-project': 'redseawatcher',
    'Authorization': 'Bearer ' + token
}

response = requests.post(request_url, data=data_json, headers=headers)

print(response.text)
#words_result = responses['textAnnotations']
try:
    token_info = response.json()
    for i in token_info['responses']:
        for words in i['textAnnotations']:
            description = words['description']
            break
    texts = description.splitlines()
except ValueError:
    print("can't convert:" + text)
