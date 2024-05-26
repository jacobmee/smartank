# Importing Image class from PIL module
from PIL import Image  # type: ignore
from datetime import datetime

import subprocess
import base64
import requests  # type: ignore
import json
import os
import logging


def get_logger():
    logger = logging.getLogger("MeterWatcher")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    fileHandler = logging.FileHandler(
        os.path.join(os.path.dirname(__file__), "smartank.log"), "a"
    )
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    return logger


logger = get_logger()


def text_recognizing(jpg):
    request_url = "https://vision.googleapis.com/v1/images:annotate"
    f = open(jpg, "rb")
    img = base64.b64encode(f.read())

    data = {
        "requests": [
            {
                "image": {"content": img.decode("utf-8")},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
            }
        ]
    }
    data_json = json.dumps(data)

    output = subprocess.check_output(
        ["/home/pi/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"]
    )
    token = output.decode("utf-8").strip()
    if not token:
        logger.error("Returned token is empty!")
        return ""

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "x-goog-user-project": "redseawatcher",
        "Authorization": "Bearer " + token,
    }

    response = requests.post(request_url, data=data_json, headers=headers)

    token_info = response.json()
    for i in token_info["responses"]:
        for words in i["textAnnotations"]:
            description = words["description"]
            break
    texts = description.splitlines()
    return texts


def getPH(numbers):  # From words into PH
    if numbers > 9 and numbers < 10:  # something it reads 8 to 9
        numbers -= numbers
    return "PH {:.1f}".format(numbers)


def getTemperature(numbers):  # From words into temperature
    return "T {:.0f}".format(numbers)


def getORP(numbers):  # From words into ORP
    return "ORP {:.0f}".format(numbers)


def value_populating(texts):

    metrics = ""
    log_info_value = ""

    for orignial_text in texts:
        converted_text = ""

        # Clean invalid data
        processing_text = orignial_text.replace(" ", "")  # remove all the spaces
        processing_text = processing_text.replace("B", "8")  # sometime 8 goes B

        try:
            numbers = float(processing_text)
            if numbers.is_integer():
                if numbers < 20:
                    converted_text = getPH(numbers)
                    metrics = metrics + converted_text + "\\n"
                elif numbers > 70 and numbers < 90:
                    converted_text = getPH(numbers / 10.0)
                    metrics = metrics + converted_text + "\\n"
                elif numbers > 20 and numbers < 30:
                    converted_text = getTemperature(numbers)
                    metrics = metrics + converted_text + "\\n"
                elif numbers > 200 and numbers < 500:
                    converted_text = getORP(numbers)
                    metrics = metrics + converted_text + "\\n"
            else:
                converted_text = getPH(numbers)
                metrics = metrics + converted_text + "\\n"

            log_info_value = (
                log_info_value + "[" + converted_text + ',' + orignial_text + ']'
            )

        except ValueError:
            logger.debug("dropping:" + orignial_text)

    logger.info(log_info_value)

    return metrics


def capturePicture():
    image_file = os.path.join(os.path.dirname(__file__), "static/images/image.jpg")
    response = subprocess.call(["raspistill", "-o", image_file])

    metrics = ""

    if response < 0:
        raise SystemExit("Error: ")

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

    Image_Name = os.path.join(
        os.path.dirname(__file__), "static/images/redsea_monitor." + str(now) + ".jpg"
    )
    Final_Image.save(Image_Name)

    # Remove the full image
    os.remove(image_file)

    return Image_Name


def save_data(metrics):
    # Read token from file
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = '{"time":"' + now + '","content":"' + metrics + '"}\n'
    data_file = os.path.join(os.path.dirname(__file__), "meter.data")
    with open(data_file, "a") as file:
        file.write(data)


def main() -> None:
    try:
        image_name = capturePicture()
        texts = text_recognizing(image_name)
        metrics = value_populating(texts)
        save_data(metrics)
    except ValueError:
        logger.error("can't convert:")
    except KeyError:
        logger.error("can't parse, token expired? ")


if __name__ == "__main__":
    main()
