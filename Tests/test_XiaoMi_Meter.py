from bluepy import btle
from dataclasses import dataclass
import time

# MAC address of the device
#mac = "a4:c1:38:86:94:99"
mac = "a4:c1:38:4b:3c:bc"
'''
Charactersitic Characteristic <ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6>
 - UUID: ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6
 - Handle: 54
 - Properties: READ NOTIFY
 - Value: b'\x00\x00\x00'
 '''

@dataclass
class Result:
    temperature: float
    humidity: int
    voltage: float
    battery: int = 0


class Measure(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        try:
            result = Result(0, 0, 0, 0)
            print(f"Data: {data}")
            temperature = int.from_bytes(data[0:2],byteorder='little',signed=True)/100
            #print(f"Temp: {temperature}")
            humidity = int.from_bytes(data[2:3],byteorder='little')
            #print(f"Hum: {humidity}")
            voltage=int.from_bytes(data[3:5],byteorder='little') / 1000.
            #print(f"Voltage: {voltage}")
            battery = round((voltage - 2) / (3.261 - 2) * 100, 2)
            #print(f"Battery: {battery}")
            result.temperature = temperature
            result.humidity = humidity
            result.voltage = voltage
            result.battery = battery
            print(result)
        except Exception as e:
            print(e)

class Connect:
    def __init__(self):
        self.measure = Measure("mijia")

    def connect(self):
        print("Connecting...")
        self.measure.temperature = None
        p = btle.Peripheral(mac)
        
        p.writeCharacteristic(0x0038, b"\x01\x00", True)
        p.writeCharacteristic(0x0046, b"\xf4\x01\x00", True)
        self.measure = Measure("mijia")
        p.withDelegate(self.measure)
        return p
    
    def getTemperature(self):
        return self.measure.temperature
    
if __name__ == "__main__":
    p = Connect().connect()
    while True:
        if p.waitForNotifications(1.0):
            continue
        print("Waiting...")
        time.sleep(1)

    p.disconnect()
    print("Disconnected")   
