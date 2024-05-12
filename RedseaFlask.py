# Importing Image class from PIL module
from flask import Flask
import requests
import json
import os


app = Flask(__name__)


@app.route("/metrics")
def metrics():

    # Read token from file
    data_file = os.path.join(os.path.dirname(__file__), 'meter.data')

    with open(data_file, "r") as file:
        data_json = file.readlines()[-1]

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

    with open(log_file, 'r') as file:
        log = file.read()

    if not log:
        return "Empty data", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    return log, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route("/log")
def log():
    # Read token from file
    log_file = os.path.join(os.path.dirname(__file__), 'smartank.log')

    with open(log_file, 'r') as file:
        log = file.read()

    if not log:
        return "Empty log", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    return log, 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == "__main__":
    app.run(debug=True, port=6001, host='0.0.0.0')
