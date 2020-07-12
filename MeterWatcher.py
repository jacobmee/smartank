import cv2
import pytesseract
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image, ImageEnhance, ImageFilter

camera = PiCamera()
camera.start_preview()
camera.capture('image.jpg')
camera.stop_preview()

# open the "original" image
orig_image = cv2.imread('image.jpg')
orig_image = cv2.rotate(orig_image, cv2.ROTATE_180)
gray = cv2.cvtColor(orig_image, cv2.COLOR_BGR2GRAY)

# Morph open to remove noise and invert image
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel, iterations=1)
cv2.imwrite('image_pre.jpg', opening)

######################
####     ORP      ####
######################
# capture the area of the text to "read" by setting "top left" and "right bottom" values in the image
left   = 420
top    = 780
right  = left + 360
bottom = top + 200

# copy the captured area
#blur = cv2.GaussianBlur(gray.copy(), (1,1), 0)
opening = cv2.threshold(opening.copy(), 0, 255, cv2.THRESH_BINARY_INV)[1]
image = opening[top:bottom,left:right]
cv2.imwrite('code_ORP.jpg', image)
text = pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

# print result from your OCR-reading
ORP = text
print(ORP)

######################
####     PH       ####
######################
# capture the area of the text to "read" by setting "top left" and "right bottom" values in the image
left   = 1600
top    = 160
right  = left + 380
bottom = top + 220

# copy the captured area
blur = cv2.GaussianBlur(opening.copy(), (5,5), 0)
opening = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
image = opening[top:bottom,left:right]
cv2.imwrite("code_PH.jpg", image)
text = pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=.0123456789')

# print result from your OCR-reading
PH = text
print(PH)

######################
##   TEMPERATURE  ####
######################
# capture the area of the text to "read" by setting "top left" and "right bottom" values in the image
left   = 1600
top    = 350
right  = left + 380
bottom = top + 200

# copy the captured area
blur = cv2.GaussianBlur(opening.copy(), (5,5), 0)
opening = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
image = opening[top:bottom,left:right]
cv2.imwrite("code_t.jpg", image)
text = pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=.0123456789')

# print result from your OCR-reading
T = text
print(T)
