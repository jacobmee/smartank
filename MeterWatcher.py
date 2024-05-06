# Importing Image class from PIL module
from PIL import Image, ImageEnhance
from datetime import datetime
from flask import Flask

import subprocess
import base64
import requests
import json
import os
import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), 'smartank.log'),
    filemode="w",datefmt='%Y-%m-%d %H:%M:%S')


# Baidu API get token
def get_token ():
	# Key and secret
    API_KEY = 'ctBuA0fMObgMHegCTSKCOKHE'
    SECRET_KEY = 'xbl7qH58ayTgc8fDuXqUH1wulQ0UGgsG'

    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


# Baidu API to recoginize the pic
def AI_recognizing (jpg):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"
    f = open(jpg, 'rb')
    img = base64.b64encode(f.read())

    params = {"image":img}
    access_token = get_token()
    request_url = request_url + "?access_token=" + access_token
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.post(request_url, data=params, headers=headers)

    #print (response)

    words_result = ""
    if response:
        token_info = response.json()
        #print (token_info)
        num = token_info['words_result_num']
        if num > 0:
            words_result = token_info['words_result']
            #print (str(len(words_result)) + ":" + json.dumps(words_result))
            return words_result

    return ""

# To analysis the return values
def value_populating (words_result):
    metrics = ""
    info_value = ""
    
    for i in words_result:
        words = i['words']
        words = words.strip()
        value = ""

        if words.isdigit():
            numbers = float(words)
            if numbers < 10 :
                value = getPH(numbers)
                metrics = metrics + value + "\n"
            elif numbers > 70 and numbers < 88 :
                value = getPH(numbers/10)
                metrics = metrics + value + "\n"
            elif numbers > 20 and numbers < 30 :
                value = getTemperature(numbers)
                metrics = metrics + value + "\n"
            elif numbers > 200 and numbers < 500 :
                value = getORP(numbers)
                metrics = metrics + value + "\n"

            info_value = info_value + "[" + words + " => " + value + "] "

    logging.info(info_value)

    return metrics

# From words into PH
def getPH (numbers):    
    if numbers == 1:
        numbers = 8.1
    elif numbers == 2:
        numbers = 8.2
    return "PH {:.1f}".format(numbers)
    

# From words into temperature
def getTemperature (numbers):
    return "T {:.0f}".format(numbers)
    

# From words into ORP
def getORP (numbers):
    return "ORP {:.0f}".format(numbers)


#######################
#######################
#__main__

app = Flask(__name__)

@app.route("/metrics")
def metrics():

    image_file= os.path.join(os.path.dirname(__file__), 'images/image.jpg')
    response = subprocess.call(["raspistill", "-o", image_file])

    metrics = ""
    if response == 0:

        # Opens a image in RGB mode
        Original_Image = Image.open(image_file)

        Rotated_Image = Original_Image.rotate(270,expand=1) 
        # Size of the image in pixels (size of original image)
        # (This is not mandatory)
        width, height = Rotated_Image.size

        # Setting the points for cropped image
        left = 0 
        top = 17 * height / 28
        right = width
        bottom = height

        # Cropped image of above dimension
        # (It will not change original image)
        Final_Image = Rotated_Image.crop((left, top, right, bottom))

        ######################
        # Generating Redsea
        ######################
        # datetime object containing current date and time
        now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        Image_Name = os.path.join(os.path.dirname(__file__), 'images/redsea_monitor.'+str(now)+'.jpg')
        Final_Image.save(Image_Name)

        # Baidu API calls
        words_result = AI_recognizing(Image_Name)
        metrics = value_populating(words_result)
        #print (metrics)

    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == "__main__":
    app.run(debug=True, port=6001, host='0.0.0.0')