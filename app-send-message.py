import artikcloud
from artikcloud.rest import ApiException
import sys, getopt
import time, random, json
from pprint import pprint
from DHT11_Python import dht11
import RPi.GPIO as GPIO
import datetime

# SDK reference for more details
# https://github.com/artikcloud/artikcloud-python
def main(argv):

        # initialize GPIO                                                                        
        GPIO.setwarnings(False)                                                                   
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        # read data using pin 14                                                                  
        instance = dht11.DHT11(pin=17)
 
	DEFAULT_CONFIG_PATH = 'config/config.json'

	with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
		config = json.load(config_file)['temperatureSensor']
	print(config)

	# Configure Oauth2 access_token for the client application.  Here we have used
	# the device token for the configuration
	artikcloud.configuration = artikcloud.Configuration();
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
            device_message['onTemp'] = (result.temperature*1.8 + 32)
            humidity = result.humidity
            print("Last valid input: " + str(datetime.datetime.now()))
            print("Temperature: %d F" % (result.temperature*1.8 + 32))
            print("Humidity: %d %%" % result.humidity)

        time.sleep(1)

	# Set the 'device id' - value from your config.json file
	device_sdid = config['deviceId']

	# set your custom timestamp
	ts = None

	# Construct a Message object for your request
	data = artikcloud.Message(device_message, device_sdid, ts) 

	try: 
	    # Debug Print oauth settings
	    pprint(artikcloud.configuration.auth_settings())

	    # Send Message
	    api_response = api_instance.send_message(data)
	    pprint(api_response)
	except ApiException as e:
	    pprint("Exception when calling MessagesApi->send_message: %s\n" % e)

        if (humidity > 0):
            device_message = {}
            device_message['humidity'] = humidity
            
            data = artikcloud.Message(device_message, device_sdid, ts)

            try:
               # Debug Print oauth settings
               pprint(artikcloud.configuration.auth_settings())

               # Send Message
               api_response = api_instance.send_message(data)
               pprint(api_response)
            except ApiException as e:
               pprint("Exception when calling MessagesApi->send_message: %s\n" % e)
 
if __name__ == "__main__":
   main(sys.argv[1:])
