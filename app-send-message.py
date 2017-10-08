import artikcloud
from artikcloud.rest import ApiException
import sys, getopt
import time, random, json
from pprint import pprint
from DHT11_Python import dht11
import RPi.GPIO as GPIO
#import Adafruit_BMP.BMP085 as BMP085
import Adafruit_ADS1x15
import datetime

def send_message(api_instance, device_message, device_sdid):
   
   # Custom timestamp
   ts = None
   data = artikcloud.Message(device_message, device_sdid, ts)
   
   # Debug Print oauth settings
   pprint(artikcloud.configuration.auth_settings())
   try:
      # Send Message
      api_response = api_instance.send_message(data)
      pprint(api_response)
   except ApiException as e:
      pprint("Exception when calling MessagesApi->send_message: %s\n" % e)

# SDK reference for more details
# https://github.com/artikcloud/artikcloud-python
def main(argv):

    # initialize GPIO                                                                        
    GPIO.setwarnings(False)                                                                   
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    # read data using pin 14

    # Initialize the ADS1115 ADC (16-bit) instance
    adc = Adafruit_ADS1x15.ADS1115()

    # Note you can change the I2C address from its default (0x48), and/or the I2C
    # bus by passing in these optional parameters:
    #adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

    # Choose a gain of 1 for reading voltages from 0 to 4.09V.
    # Or pick a different gain to change the range of voltages that are read:
    #  - 2/3 = +/-6.144V
    #  -   1 = +/-4.096V
    #  -   2 = +/-2.048V
    #  -   4 = +/-1.024V
    #  -   8 = +/-0.512V
    #  -  16 = +/-0.256V
    # See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
    GAIN = 1                                                                  

    instance = dht11.DHT11(pin=17)
 
    DEFAULT_CONFIG_PATH = 'config/config.json'

    with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
        config = json.load(config_file)['temperatureSensor']
    print(config)

    # Configure Oauth2 access_token for the client application.  Here we have used
    # the device token for the configuration
    artikcloud.configuration = artikcloud.Configuration()
    artikcloud.configuration.access_token = config['deviceToken']

    # We create an instance of the Message API class which provides
    # the send_message() and get_last_normalized_messages() api call
    # for our example
    api_instance = artikcloud.MessagesApi()

    # Device_message - data that is sent to your device
    device_message = {}

    # We send random values to the 'temp' field for this FireSensor.  
    # Let's send a random value between 0 and 200 for this demo.
    #device_message['temp'] = random.randrange(0,200);
    result = instance.read()
        
    humidity = 0
    if result.is_valid():
       device_message['temp'] = (result.temperature*1.8 + 32)
       humidity = result.humidity
       print("Last valid input: " + str(datetime.datetime.now()))
       print("Temperature: %d F" % (result.temperature*1.8 + 32))
       print("Humidity: %d %%" % result.humidity)

    time.sleep(1)

    # Set the 'device id' - value from your config.json file
    device_sdid = config['deviceId']
    send_message(api_instance, device_message, device_sdid)

    if (humidity > 0):
       device_message = {}
       device_message['humidity'] = humidity
       send_message(api_instance, device_message, device_sdid)

    #sensor = BMP085.BMP085()
    #pressure = sensor.read_pressure()
    #print('Pressure = {0:0.2f} Pa'.format(pressure))
    air_qa_value = adc.read_adc(0, gain=GAIN)
    print ("Air quality: %f " % air_qa_value)    

    if (air_qa_value > 0):
        device_message = {}
        device_message['air_quality'] = air_qa_value
    #if (pressure > 0):
    #   device_message = {}
    #   device_message['pressure'] = pressure
        send_message(api_instance, device_message, device_sdid)

        
if __name__ == "__main__":
   main(sys.argv[1:])

