# Importing Image class from PIL module
from flask import Flask
import requests
import json
import os


def tail(f, lines=80):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            f.seek(block_number * BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0, 0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return b'\n'.join(all_read_text.splitlines()[-total_lines_wanted:])


app = Flask(__name__)


@app.route("/metrics")
def metrics():

    # Read token from file
    data_file = os.path.join(os.path.dirname(__file__), 'meter.data')

    with open(data_file, "rb") as file:
        data_json = tail(file, 1).decode("utf-8")

    data = json.loads(data_json)

    date = data["time"]
    value = data["content"]

    if not metrics:
        return "Empty log", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    return value, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/data")
def data():
    # Read token from file
    log_file = os.path.join(os.path.dirname(__file__), 'meter.data')

    with open(log_file, 'rb') as file:
        data = tail(file).decode("utf-8")

    if not data:
        return "Empty data", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    return data, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/log")
def log():
    # Read token from file
    log_file = os.path.join(os.path.dirname(__file__), 'smartank.log')

    with open(log_file, 'rb') as file:
        log = tail(file).decode("utf-8")

    if not log:
        return "Empty log", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    return log, 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == "__main__":
    app.run(debug=True, port=6001, host='0.0.0.0')
