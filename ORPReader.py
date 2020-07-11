
from flask import Flask
''' Raspberry Pi, ADS1115, PH4502C Calibration '''
import board
import busio
import time
import sys
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

app = Flask(__name__)

@app.route("/metrics")
def metrics():
    # Create an ADS1115 ADC (16-bit) instance.
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)

    channel = None
    channel = AnalogIn(ads, ADS.P0)

    OFFSET = 10
    voltage_samples = list()

    # Get average data for voltage
    for i in range(10): # Take 10 samples
        voltage_samples.append(channel.voltage)
    voltage_samples.sort() # Sort samples and discard highest and lowest
    voltage_samples = voltage_samples[2:-2]
    voltage = (sum(map(float,voltage_samples))/6) # Get average value from remaining 6

    # Calculate the ORP value from voltage
    voltage = voltage * 1000
    ORP = 2000 - voltage - OFFSET

    # Output to Flask
    metrics = "ORP {:.1f}".format(ORP)
    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
