import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import base64
import requests
import json
from datetime import datetime

def resize(rawimg):  # resize img to 28*28
    fx = 100.0 / rawimg.shape[0]
    fy = 100.0 / rawimg.shape[1]
    fx = fy = min(fx, fy)
    img = cv2.resize(rawimg, None, fx=fx, fy=fy, interpolation=cv2.INTER_CUBIC)

    return img

def crop(rawimg, top, bottom, left, right):  # resize img to 28*28
    rawimg = rawimg[top:bottom,left:right].copy()
    return rawimg

######################
####    Camera    ####
######################
#JPG = 'redsea.2020-10-16_15:29:09.jpg'
#JPG = 'redsea.2020-10-16_15:30:05.jpg'
JPG = 'redsea-09.jpg'
# open the "original" image
orig_image = cv2.imread(JPG)

######################
#  Generating  ORP numbers
######################

x = 170
y = 105
value = [255, 255, 255]
outimge = crop(orig_image, 25, 25+x, 72, 72+y)
dst = cv2.copyMakeBorder(outimge, 0, 0, 33, 32, cv2.BORDER_CONSTANT, None, value)
cv2.imwrite("1.jpg", resize(dst))
outimge = crop(orig_image, 25, 25+x, 178, 178+y)
dst = cv2.copyMakeBorder(outimge, 0, 0, 33, 32, cv2.BORDER_CONSTANT, None, value)
cv2.imwrite("2.jpg", resize(dst))
outimge = crop(orig_image, 25, 25+x, 282, 282+y)
dst = cv2.copyMakeBorder(outimge, 0, 0, 33, 32, cv2.BORDER_CONSTANT, None, value)
cv2.imwrite("3.jpg", resize(dst))

######################
#  Generating  PH numbers
######################
x = 200
y = 115
outimge = crop(orig_image, 220, 190+x, 180, 180+y)
dst = cv2.copyMakeBorder(outimge, 0, 0, 33, 32, cv2.BORDER_CONSTANT, None, value)
cv2.imwrite("4.jpg", resize(dst))
outimge = crop(orig_image, 220, 190+x, 310, 310+y)
dst = cv2.copyMakeBorder(outimge, 0, 0, 33, 32, cv2.BORDER_CONSTANT, None, value)
cv2.imwrite("5.jpg", resize(dst))


######################
#  Generating  T numbers
######################
x = 100
y = 65
outimge = crop(orig_image, 430, 430+x, 242, 242+y)
dst = cv2.copyMakeBorder(outimge, 0, 0, 17, 18, cv2.BORDER_CONSTANT, None, value)
cv2.imwrite("6.jpg", resize(dst))
outimge = crop(orig_image, 430, 430+x, 320, 320+y)
dst = cv2.copyMakeBorder(outimge, 0, 0, 17, 18, cv2.BORDER_CONSTANT, None, value)
cv2.imwrite("7.jpg", resize(dst))
