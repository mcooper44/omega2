'''
methods for onewire mqtt connected 
temperature sensors
'''

# import standard lib and installed modules
import time
import json
import paho.mqtt.client as mqtt

# import modules that are a part of this project
from temperatureSensor import TemperatureSensor
import oneWire
from json_config import configuration

SERVICE_ONE = 0 # INDEX FOR SERVICE IN THE LIST
SERVICE_TWO = 1

# setup onewire and polling interval
oneWireGpio = 19 # set the sensor GPIO
pollingInterval = 25 #  int - representing seconds

# load configuration file. Omega2 py install cannot run yaml
# so load config in json format
node = configuration('config.json')

# info necessary for mqtt
b_name, c_name = node.get_client() # broker and client name
#device = node.get_device_by_type('temp')
mqtt_service = node.service_list[SERVICE_ONE] # mqtt service path a/b/c
#mqtt_service = node.service_list[SERVICE_TWO]

# add code to extract datastructures from config file that can be iteratedt through
# to add all the services with the correct values in them

def on_message(client, userdata, message):
    '''
    call back function for the mqtt client
    prints out the message recieved from the broker when a message
    is published
    '''

    print('message recieved {}'.format(message.payload.decode('utf-8')))
    print('message topic= {}'.format(message.topic))
    print('message quality of service={}'.format(message.qos))

def __main__():
    # check if 1-Wire is setup in the kernel
    if not oneWire.setupOneWire(str(oneWireGpio)):
        print("Kernel module could not be inserted. Please reboot and try again.")
        return -1

    # get the address of the temperature sensor
    #   it should be the only device connected in this experiment    
    sensorAddress = oneWire.scanOneAddress() # NEED TO CHANGE THIS FOR HANDLING MORE THAN ONE SERVICE

    # instantiate the temperature sensor object
    sensor = TemperatureSensor()
    sensor.add_sensor("oneWire", {"address":sensorAddress, "gpio": oneWireGpio})
    ok_to_talk = sensor.ask_status(sensorAddress)
    if not ok_to_talk:
        print("Sensor was not set up correctly. Please make sure that your sensor is firmly connected to the GPIO specified above and try again.")
        return -1

    client = mqtt.Client(c_name)
    #client.on_message=on_message # attaching function to grab callback
    client.connect(b_name)
    client.loop_start()
    client.subscribe(mqtt_service) # a/b/c - sensor
    print('connected to {} and subscribed to {}'.format(b_name, mqtt_service))
    print('loop started')
    # infinite loop - runs main program code continuously
    try:
        while True:
	    # check and print the temperature
            value = sensor.read_sensor(sensorAddress)
            rp = {'sensor': mqtt_service,
                  'reading': str(value)}
            rpj = json.dumps(rp)
            client.publish(mqtt_service, rpj)
            print("T = " + str(value) + " C")
            time.sleep(pollingInterval) # should be at least 4-5 seconds
    except (ValueError, EOFError, KeyboardInterrupt) as e:
        print('encountered {}'.format(e))
        client.loop_stop()
        client.disconnect()
        print('shutdown')

if __name__ == '__main__':
    __main__()