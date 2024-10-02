from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config
import json
import time
import ADC0832
import math

# Initialize the ADC0832
def init_sensors():
    ADC0832.setup()

# Function to read temperature from the sensor
def read_temperature():
    res = ADC0832.getADC(0)
    Vr = 3.3 * float(res) / 255
    Rt = 10000 * Vr / (3.3 - Vr)
    temp = 1 / (((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
    Cel = temp - 273.15
    return Cel

# Function to read voltage from the second sensor
def read_voltage():
    res = ADC0832.getADC(1)  # Assuming second sensor is on ADC channel 1
    voltage = 5 / 255 * res
    return voltage

# User specified callback function
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Configure the MQTT client
myMQTTClient = AWSIoTMQTTClient(config.CLIENT_ID)
myMQTTClient.configureEndpoint(config.AWS_HOST, config.AWS_PORT)
myMQTTClient.configureCredentials(config.AWS_ROOT_CA, config.AWS_PRIVATE_KEY, config.AWS_CLIENT_CERT)
myMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
myMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)

# Connect to MQTT Host
if myMQTTClient.connect():
    print('AWS connection succeeded')

# Subscribe to topic
myMQTTClient.subscribe(config.TOPIC, 1, customCallback)
time.sleep(2)

# Initialize sensors
init_sensors()

# Collect and send data every 10 seconds
try:
    while True:
        temperature = read_temperature()
        voltage = read_voltage()  # Read voltage from the second sensor
        payload = json.dumps({
            "temperature": temperature,
            "voltage": voltage
        })
        myMQTTClient.publish(config.TOPIC, payload, 1)
        print(f"Sent: {payload} to {config.TOPIC}")
        time.sleep(10)  # Wait for 10 seconds
except KeyboardInterrupt:
    ADC0832.destroy()
    print('The end !')
