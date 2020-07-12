import cv2
import pytesseract
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from flask import Flask
import base64
import requests

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

def get_words (jpg):
    #request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    f = open(jpg, 'rb')
    img = base64.b64encode(f.read())

    params = {"image":img}
    access_token = get_token()
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    token_key = ""
    if response:
        token_info = response.json()
        #print (token_info)
        num = token_info['words_result_num']
        if num > 0:
            token_key = token_info['words_result']
            print (token_key)
            return token_key

    return ""

app = Flask(__name__)

@app.route("/metrics")
def metrics():

    camera = PiCamera()
    camera.start_preview()
    camera.capture('image.jpg')
    camera.stop_preview()
    camera.close()

    # open the "original" image
    orig_image = cv2.imread('image.jpg')
    orig_image = cv2.rotate(orig_image, cv2.ROTATE_180)

    ######################
    ####     ORP      ####
    ######################
    # capture the area of the text to "read" by setting "top left" and "right bottom" values in the image
    left   = 360
    top    = 770
    right  = left + 440
    bottom = top + 200

    JPG = 'code_ORP.jpg'
    orp_image = orig_image[top:bottom,left:right].copy()
    orp_image = cv2.cvtColor(orp_image, cv2.COLOR_BGR2GRAY)
    orp_image = cv2.threshold(orp_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    orp_image = cv2.morphologyEx(orp_image, cv2.MORPH_OPEN, kernel, iterations=1)

    cv2.imwrite(JPG, orp_image)

    ######################
    ####     PH       ####
    ######################
    left   = 1480
    top    = 180
    right  = left + 440
    bottom = top + 200

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
    ##   TEMPERATURE  ####
    ######################
    # capture the area of the text to "read" by setting "top left" and "right bottom" values in the image
    left   = 1480
    top    = 370
    right  = left + 440
    bottom = top + 200
    JPG = 'code_t.jpg'
    t_image = orig_image[top:bottom,left:right].copy()
    t_image = cv2.cvtColor(t_image, cv2.COLOR_BGR2GRAY)
    t_image = cv2.GaussianBlur(t_image, (9,9), 0)
    t_image = cv2.threshold(t_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    cv2.imwrite(JPG, t_image)

    JPG = 'redsea.jpg'
    vis = np.concatenate((orp_image, ph_image, t_image), axis=0)
    #vis = np.concatenate((orp_image, ph_image), axis=0)
    cv2.imwrite(JPG, vis)

    words_result = get_words(JPG)
    size = len(words_result)
    metrics = ""
    if (size > 0):
        ORP = float(words_result[0]['words'])
        if ORP > 200 :
            metrics = "ORP {:.1f}".format(ORP) + "\n"

    if (size > 1):
        PH = float(words_result[1]['words'])
        if PH > 70 :
            metrics = metrics + "PH {:.1f}".format((PH/10)) + "\n"
        if PH == 19 or PH == 9:
            metrics = metrics + "PH 7.9\n"
        if PH > 8 and PH < 9 :
            metrics = metrics + "PH {:.1f}".format(PH) + "\n"
        if PH == 24 or PH == 25 or PH == 26:
            metrics = metrics + "T {:.1f}".format(PH) + "\n"

    if (size > 2):
        T = float(words_result[2]['words'])
        metrics = metrics + "T {:.1f}".format(T) + "\n"

    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(debug=True, port=6001, host='0.0.0.0')
