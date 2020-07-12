import cv2
import pytesseract
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image, ImageEnhance, ImageFilter
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
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"
    # 二进制方式打开图片文件
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
        num = token_info['words_result_num']
        if num > 0:
            words_result = token_info['words_result']
            token_key = words_result[0]['words']
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
    ####     PH       ####
    ######################
    left   = 1600
    top    = 160
    right  = left + 380
    bottom = top + 220

    # copy the captured area

    JPG = 'code_ph.jpg'
    gray = cv2.cvtColor(orig_image.copy(), cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    opening = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    image = opening[top:bottom,left:right]
    cv2.imwrite(JPG, image)

    PH = get_words(JPG)
    metrics = "PH " + PH
    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(debug=True, port=6002, host='0.0.0.0')
