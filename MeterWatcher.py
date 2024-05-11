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


def get_logger():
    logger = logging.getLogger("MeterWatcher")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")

    fileHandler = logging.FileHandler(os.path.join(
        os.path.dirname(__file__), 'smartank.log'), "w")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    return logger


logger = get_logger()


def baidu_get_token():
    # Key and secret
    API_KEY = 'ctBuA0fMObgMHegCTSKCOKHE'
    SECRET_KEY = 'xbl7qH58ayTgc8fDuXqUH1wulQ0UGgsG'

    url = "https://aip.baidubce.com/oauth/2.0/token"

    params = {"grant_type": "client_credentials",
              "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


def baidu_AI_recognizing(jpg):
    # URL for baidu recoginize
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    f = open(jpg, 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img}
    access_token = baidu_get_token()
    request_url = request_url + "?access_token=" + access_token

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.post(request_url, data=params, headers=headers)

    words_result = None
    num = 0
    if response:
        token_info = response.json()
        num = token_info['words_result_num']
        if num > 0:
            words_result = token_info['words_result']

    texts = []
    for i in words_result:
        words = i["words"]
        texts += [words]

    return texts


def google_AI_recognizing(jpg):
    # URL for baidu recoginize
    request_url = "https://vision.googleapis.com/v1/images:annotate"
    f = open(jpg, 'rb')
    img = base64.b64encode(f.read())

    data = {"requests": [{"image": {"content": img.decode(
        "utf-8")}, "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]}]}
    data_json = json.dumps(data)

    # Read token from file
    token_file = os.path.join(os.path.dirname(__file__), 'token.file')

    with open(token_file, 'r') as file:
        token = file.read().strip()

    if not token:
        logger.error("token.file is empty!")
        return ""

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-goog-user-project': 'redseawatcher',
        'Authorization': 'Bearer ' + token
    }

    response = requests.post(request_url, data=data_json, headers=headers)

    try:
        token_info = response.json()
        for i in token_info['responses']:
            for words in i['textAnnotations']:
                description = words['description']
                break
        texts = description.splitlines()
    except ValueError:
        logger.error("can't convert:" + text)
    except KeyError:
        logger.error("can't parse:" + response.text)

    return texts


def value_populating(texts):

    metrics = ""
    log_info_value = ""

    for orignial_text in texts:
        converted_text = None

        # Clean invalid data
        processing_text = orignial_text.replace(' ', '')  # remove all the spaces
        processing_text = processing_text.replace('B', '8')  # sometime 8 goes B

        try:
            numbers = float(processing_text)
            if numbers.is_integer():
                if numbers < 20:
                    converted_text = getPH(numbers)
                    metrics = metrics + converted_text + "\n"
                elif numbers > 70 and numbers < 90:
                    converted_text = getPH(numbers / 10.0)
                    metrics = metrics + converted_text + "\n"
                elif numbers > 20 and numbers < 30:
                    converted_text = getTemperature(numbers)
                    metrics = metrics + converted_text + "\n"
                elif numbers > 200 and numbers < 500:
                    converted_text = getORP(numbers)
                    metrics = metrics + converted_text + "\n"
            else:
                converted_text = getPH(numbers)
                metrics = metrics + converted_text + "\n"

        except ValueError:
            logger.error("can't convert:" + orignial_text)

        log_info_value = log_info_value + "[" + orignial_text + " => " + converted_text + "] "

    logger.info(log_info_value)

    return metrics


def getPH(numbers):  # From words into PH
    return "PH {:.1f}".format(numbers)


def getTemperature(numbers):  # From words into temperature
    return "T {:.0f}".format(numbers)


def getORP(numbers):  # From words into ORP
    return "ORP {:.0f}".format(numbers)


#######################
#######################
# __main__
app = Flask(__name__)


@app.route("/metrics")
def metrics():

    image_file = os.path.join(os.path.dirname(__file__), 'images/image.jpg')
    response = subprocess.call(["raspistill", "-o", image_file])

    metrics = None

    if response < 0:
        return "Can't capture images!", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    # Opens a image in RGB mode
    Original_Image = Image.open(image_file)

    Rotated_Image = Original_Image.rotate(270, expand=1)
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

    Image_Name = os.path.join(os.path.dirname(
        __file__), 'images/redsea_monitor.' + str(now) + '.jpg')
    Final_Image.save(Image_Name)

    # Remove the full image
    os.remove(image_file)

    # texts = baidu_AI_recognizing(Image_Name) # Baidu API calls
    texts = google_AI_recognizing(Image_Name)

    if not texts:
        return "No value returned", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    metrics = value_populating(texts)
    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == "__main__":
    app.run(debug=True, port=6001, host='0.0.0.0')
