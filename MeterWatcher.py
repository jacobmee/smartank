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

# Setup logger
logger = logging.getLogger("MeterWatcher")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")

fileHandler = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'smartank.log'), "w")
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)


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
    #request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
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

    words_result = ""
    if response:
        token_info = response.json()
        num = token_info['words_result_num']
        if num > 0:
            words_result = token_info['words_result']
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

        try:
            numbers = float(words)
            if numbers.is_integer():
                if numbers < 10 :
                    value = getPH(numbers)
                    metrics = metrics + value + "\n"
                elif numbers > 70 and numbers < 90 :
                    value = getPH(numbers/10.0)
                    metrics = metrics + value + "\n"
                elif numbers > 20 and numbers < 30 :
                    value = getTemperature(numbers)
                    metrics = metrics + value + "\n"
                elif numbers > 200 and numbers < 500 :
                    value = getORP(numbers)
                    metrics = metrics + value + "\n"
            else:
                value = getPH(numbers)
                metrics = metrics + value + "\n"

        except ValueError:
            logger.error("can't convert:" + words)

        info_value = info_value + "[" + words + " => " + value + "] "

    logger.info(info_value)

    return metrics

# From words into PH
def getPH (numbers):
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

        # Remove the full image
        os.remove(image_file)

        # Baidu API calls
        words_result = AI_recognizing(Image_Name)
        metrics = value_populating(words_result)

    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == "__main__":
    app.run(debug=True, port=6001, host='0.0.0.0')
