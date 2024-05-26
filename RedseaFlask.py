# Importing Image class from PIL module
from flask import Flask  # type: ignore
from flask import send_file  # type: ignore
from flask import render_template  # type: ignore
import json
import os


def tail(f, lines=40):
    total_lines_wanted = lines
    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if block_end_byte - BLOCK_SIZE > 0:
            f.seek(block_number * BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0, 0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b"\n")
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b"".join(reversed(blocks))
    return b"\n".join(all_read_text.splitlines()[-total_lines_wanted:][::-1])


app = Flask(__name__, static_url_path="/static")


@app.route("/metrics")
def metrics():

    # Read token from file
    data_file = os.path.join(os.path.dirname(__file__), "meter.data")

    with open(data_file, "rb") as file:
        data_json = tail(file, 1).decode("utf-8")

    try:
        data = json.loads(data_json)
    except Exception as e:
        value = ""

    date = data["time"]
    value = data["content"]

    if not metrics:
        value = ""

    return value, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/images")
def images():
    # Read token from file
    images = os.listdir(os.path.join(os.path.dirname(__file__), "static/images"))

    # only show images with jpg extension
    images = [image for image in images if image.endswith(".jpg")]
    images = [
        f"<li><a href='/static/images/{image}'>{image}</a></li>" for image in images
    ]

    # sort images by name reverse
    images.sort(reverse=True)

    images = images[:40]

    content = "".join(images)
    return render_template("content.html", content=content)


@app.route("/log")
def log():
    # Read token from file
    log_file = os.path.join(os.path.dirname(__file__), "smartank.log")

    with open(log_file, "rb") as file:
        log = tail(file).decode("utf-8")

    if not log:
        return "Empty log", 200, {"Content-Type": "text/plain; charset=utf-8"}

    output_list = []
    for line in log.split("\n"):
        # 2024-05-26 21:47:15 INFO: [ORP 242,242][PH 8.1,8.1][T 24,24]
        output = {"time": line[: line.find("INFO")].strip()}
        for value in line[line.find("[") :].split("]"):
            value_list = value.split(",")
            first = value_list[0].strip()
            if not first:
                continue
            orginal = value_list[1].strip()
            key = first.split(" ")[0]
            key = key[1:]
            converted = first.split(" ")[1]

            output[key + " converted"] = converted
            output[key + " orginal"] = orginal

        output_list.append(output)

    return json.dumps(output_list), 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    app.run(debug=True, port=6001, host="0.0.0.0")
