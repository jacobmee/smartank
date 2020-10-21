import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from flask import Flask
import base64
import requests
import json
from datetime import datetime
# Cache
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()
# Cache End

# Baidu API get token
def get_token ():
    client_id = 'ctBuA0fMObgMHegCTSKCOKHE'
    client_secret = 'xbl7qH58ayTgc8fDuXqUH1wulQ0UGgsG'
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret
    response = requests.get(host)
    token_key = ""
    if response:
        #print(response.json())
        token_info = response.json()
        token_key = token_info['access_token']

    return token_key

# Baidu API to recoginize the pic
def get_words (jpg):
    #request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    #request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"
    f = open(jpg, 'rb')
    img = base64.b64encode(f.read())

    params = {"image":img}
    access_token = get_token()
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    print (response)
    token_key = ""
    if response:
        token_info = response.json()
        #print (token_info)
        num = token_info['words_result_num']
        if num > 0:
            token_key = token_info['words_result']
            print (str(len(token_key)) + ":" + json.dumps(token_key))
            return token_key

    return ""

def set_cache (key, value):
    cache.set(key, value)
    #print ("Set cache " + key + ":{:.1f}".format(value))
    return value

def load_cache (key):
    value = cache.get(key)
    if value is None:
        if key == "PH":
            value = 8
        elif key == "ORP":
            value = 444.4
        elif key == "T":
            value = 25
    #print ("Load cache " + key + ":{:.1f}".format(value))
    return value

# From words into temperature
def getTemperature (words):
    words = words.strip()
    pre_T = float(load_cache("T"))
    T = 0
    if words.isdigit():
        T = float(words)
    elif words == "2S" or words == "2s":
        T = 25

    ABS = abs(T - pre_T)

    if ABS <= 2:
        return "T {:.1f}".format(set_cache("T", T)) + "\n"
    else:
        print ("abs T: {:.1f}".format(ABS) + " use cache: {:.1f}".format(pre_T))
        return "T {:.1f}".format(pre_T) + "\n"

# From words into ORP
def getORP (words):
    words = words.strip()
    pre_ORP = float(load_cache("ORP"))
    ORP = 0
    if words.isdigit():
        ORP = float(words)
    elif words == "36S" or words == "36s":
        ORP = 365

    ABS = abs(ORP - pre_ORP)
    if ABS < 200: # > 250 as minmial
        return "ORP {:.1f}".format(set_cache("ORP", ORP)) + "\n"
    else:
        print ("abs T: {:.1f}".format(ABS) + " use cache: {:.1f}".format(pre_ORP))
        return "ORP {:.1f}".format(pre_ORP) + "\n"

# From words into PH
def getPH (words):
    words = words.strip()
    pre_PH = float(load_cache("PH"))
    PH = 0
    if words.isdigit():
        PH = float(words)
        if PH > 75 and PH < 85 :
            PH = PH/10
        elif PH == 19 or PH == 9:
            PH = 7.9
        elif PH == 0:
            PH = 8.0
    elif words == "\u65e5": # 7.8 or 8.1
        PH = float(load_cache("PH"))
        if (PH <= 7.9): PH = 7.8
        elif (PH >= 8.0): PH = 8.1
    elif words == "1\u65e5": # 7.8
        PH = 7.8
    else: # not a digit, but also not PH.
     return getTemperature(words)


    ABS = abs(PH - pre_PH)

    if ABS <= 0.2:
        return "PH {:.1f}".format(set_cache("PH", PH)) + "\n"
    else:
        print ("abs T: {:.1f}".format(ABS) + " use cache: {:.1f}".format(pre_PH))
        return "PH {:.1f}".format(pre_PH) + "\n"

# To analysis the return values
def populate (words_result):
    metrics = ""

    size = len(words_result)
    #if (size >= 4 or size <= 0): # Error for reading
    #    return metrics

    if (size > 0): # ORP data
        metrics = metrics + getORP(words_result[0]['words'])

    if (size > 1): # PH Data
        metrics = metrics + getPH(words_result[1]['words'])

    if (size > 2): # T Data
        metrics = metrics + getTemperature(words_result[2]['words'])

    return metrics


#######################
#######################
#__main__

app = Flask(__name__)

@app.route("/metrics")
def metrics():

    ######################
    ####    Camera    ####
    ######################
    JPG = 'image.jpg'
    camera = PiCamera()
    camera.start_preview()
    camera.capture(JPG)
    camera.stop_preview()
    camera.close()

    # open the "original" image
    orig_image = cv2.imread(JPG)
    orig_image = cv2.rotate(orig_image, cv2.ROTATE_180)

    cv2.imwrite(JPG, orig_image)
    ######################
    #  Generating  ORP
    ######################
    left   = 100
    top    = 350
    right  = left + 180
    bottom = top + 80

    # copy the captured area
    JPG = 'code_ORP.jpg'
    orp_image = orig_image[top:bottom,left:right].copy()
    orp_image = cv2.cvtColor(orp_image, cv2.COLOR_BGR2GRAY)
    orp_image = cv2.threshold(orp_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    orp_image = cv2.morphologyEx(orp_image, cv2.MORPH_OPEN, kernel, iterations=1)

    cv2.imwrite(JPG, orp_image)

    ######################
    #  Generating  PH
    ######################
    left   = 540
    top    = 110
    right  = left + 180
    bottom = top + 80

    # copy the captured area
    JPG = 'code_ph.jpg'
    ph_image = orig_image[top:bottom,left:right].copy()
    ph_image = cv2.cvtColor(ph_image, cv2.COLOR_BGR2GRAY)
    #ph_image = cv2.GaussianBlur(ph_image, (7,7), 0)
    ph_image = cv2.threshold(ph_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    ph_image = cv2.morphologyEx(ph_image, cv2.MORPH_OPEN, kernel, iterations=1)
    cv2.imwrite(JPG, ph_image)

    ######################
    #  Generating  T
    ######################
    left   = 540
    top    = 190
    right  = left + 180
    bottom = top + 80

    # copy the captured area
    JPG = 'code_t.jpg'
    t_image = orig_image[top:bottom,left:right].copy()
    t_image = cv2.cvtColor(t_image, cv2.COLOR_BGR2GRAY)
    t_image = cv2.GaussianBlur(t_image, (9,9), 0)
    t_image = cv2.threshold(t_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    cv2.imwrite(JPG, t_image)

    ######################
    # Generating Redsea
    ######################
    # datetime object containing current date and time
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    JPG = 'redsea.'+str(now)+'.jpg'
    vis = np.concatenate((orp_image, ph_image, t_image), axis=0)
    #vis = np.concatenate((orp_image, ph_image), axis=0)
    cv2.imwrite(JPG, vis)

    # Baidu API calls
    words_result = get_words(JPG)
    size = len(words_result)
    metrics = populate(words_result)

    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(debug=True, port=6001, host='0.0.0.0')
