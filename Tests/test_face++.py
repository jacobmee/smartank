
import subprocess
import base64
import requests
import json
import os
import logging


# URL for baidu recoginize
request_url = "https://api-cn.faceplusplus.com/imagepp/v2/generalocr"
jpg = "images/7.9.jpg"
f = open(jpg, 'rb')
img = base64.b64encode(f.read())

request_url = request_url

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
}

"""
curl -X POST "https://api-cn.faceplusplus.com/imagepp/v1/recognizetext" \
-F "api_key=KwEun0LOHJV1pKKfN6e0NDdpE5RQEeOc" \
-F "api_secret=nrUA33mS7tTh1dZ_HWI4bQoTY1z-hHC9" \
-F "image_file=@image/7.9.jpg"
"""


params = {"api_key": "KwEun0LOHJV1pKKfN6e0NDdpE5RQEeOc",
          "api_secret": "nrUA33mS7tTh1dZ_HWI4bQoTY1z-hHC9",
          "image_base64": img}

response = requests.post(request_url, data=params, headers=headers)

print(response.text)
