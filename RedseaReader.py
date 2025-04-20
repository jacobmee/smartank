# Importing Image class from PIL module
from PIL import Image  # type: ignore
from datetime import datetime
from openai import OpenAI

import subprocess
import base64
import requests  # type: ignore
import json
import os
import logging


def get_logger():
    logger = logging.getLogger("MeterWatcher")
    logger.setLevel(logging.DEBUG)

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

def getPH(numbers):  # From words into PH
    return "PH {:.1f}".format(numbers)

def getTemperature(numbers):  # From words into temperature
    return "T {:.0f}".format(numbers)

def getORP(numbers):  # From words into ORP
    return "ORP {:.0f}".format(numbers)

def google_value_populating(texts):

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

def google_visioning(jpg):
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
    
    return google_value_populating(texts)


def kimi_visioning(jpg):
    client = OpenAI(
        api_key="sk-agJiLcSiRQQDC8fsn0e0yZbNmyoZylWCj9aYI10svj2ovgrv",
        base_url="https://api.moonshot.cn/v1",
    )
 
    # 在这里，你需要将 kimi.png 文件替换为你想让 Kimi 识别的图片的地址
    
    with open(jpg, "rb") as f:
        image_data = f.read()
    
    # 我们使用标准库 base64.b64encode 函数将图片编码成 base64 格式的 image_url
    image_url = f"data:image/{os.path.splitext(jpg)[1]};base64,{base64.b64encode(image_data).decode('utf-8')}"
    
    
    completion = client.chat.completions.create(
        model="moonshot-v1-8k-vision-preview",
        messages=[
            {"role": "system", "content": "你是 Kimi。"},
            {
                "role": "user",
                # 注意这里，content 由原来的 str 类型变更为一个 list，这个 list 中包含多个部分的内容，图片（image_url）是一个部分（part），
                # 文字（text）是一个部分（part）
                "content": [
                    {
                        "type": "image_url", # <-- 使用 image_url 类型来上传图片，内容为使用 base64 编码过的图片内容
                        "image_url": {
                            "url": image_url,
                        },
                    },
                    {
                        "type": "text",
                        "text": "图片里右上角有个PH值(7.7-8.5之间)和温度(20-28之间)，左下角是ORP值(200-450之间)，请以ORP:ORP值,PH:PH值,T:温度值的格式输出", # <-- 使用 text 类型来提供文字指令，例如“描述图片内容”
                    },
                ],
            },
        ],
    )

    
    #print(completion.choices[0].message.content)
    texts = completion.choices[0].message.content.split(",")

    #KIMI response: ORP 364, PH 8.2, T 25
    metrics = ""
    log_info_value = ""

    try:
        for orignial_text in texts:
            pair = orignial_text.replace(" ", "")
            name = pair.split(":")[0]
            value = pair.split(":")[1]
            #print("name: %s, value: %s" % (name, value))
            if name == "ORP":
                converted_text = getORP(float(value))
                metrics = metrics + converted_text + "\\n"
            elif name == "PH":
                converted_text = getPH(float(value))
                metrics = metrics + converted_text + "\\n"
            elif name == "T":
                converted_text = getTemperature(float(value))
                metrics = metrics + converted_text + "\\n"
        
            log_info_value = (
                    log_info_value + "[" + converted_text + ',' + value + ']'
                )
            
        logger.info(log_info_value)
    except ValueError:
        logger.debug("dropping:" + orignial_text)
    except Exception as result:
        logger.error("unknow error, network issue? Error: %s" %result)

    return metrics

def text_recognizing(jpg):
    #return google_visioning(jpg)
    return kimi_visioning(jpg)


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
        #logger.info("texts: %s" % texts)
        save_data(texts)
    except ValueError:
        logger.error("can't convert:")
    except KeyError:
        logger.error("can't parse, token expired? ")
    except Exception as result:
        logger.error("unknow error, network issue? Error: %s" %result)


if __name__ == "__main__":
    main()
