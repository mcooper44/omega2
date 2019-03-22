import time
import sqlite 
import paho.mqtt.client as mqtt
from mqtt_config import configuration


class listener():
    def __init__(self, client_name, broker, services, run_silent=False):
        self.client = mqtt.Client(client_name)
        self.broker = broker
        self.services = services
        self.ok_go = True
	self.run_silent = run_silent
	
        if self.client:
            self.client.on_message = listener.on_message
            self.client.on_publish = listener.on_publish
    
    @staticmethod
    def log_to_db(db, payload):
        '''
	passes the payload to the db for processing
	and storage
	'''
	pass
    
    @staticmethod
    def on_message(client, userdata, message):
        time.sleep(1)
        payload = str(message.payload.decode("utf-8"))
        if not self.run_silent:
	    print('{}'.format(payload))
	listener.log_to_db('swarm.sqlite', payload)
	
    @staticmethod
    def on_publish(client, userdata, mid):
        print('message ID: {}'.format(mid))

    def connect(self):
	'''
	Connect to the broker so that we can subscribe 
	and start recieving messages
	'''
        self.client.connect(self.broker)

    def subscribe(self):
	'''
	subscribe to the services in the list
	passed into the object when it was 
	instantiated 
	'''
        for service in self.services:
            self.client.subscribe(service)

    def loop(self):
        '''
	Invoke this method to listen to the broker
	and recieve payloads from the services 
	that the listener connected to by invoking the 
	subscribe method
	Requires that the connect() and then subscribe()
	methods were previously called
	'''
	try:
            while self.ok_go:
                self.client.loop_forever()
        except (EOFError, KeyboardInterrupt) as e:
            print('{}  <- this happened'.format(e))
            self.client.loop_stop()
            self.client.disconnect()
            self.ok_go = False

if __name__ == '__main__':
    conf = configuration('config.yaml')
    broker, services = conf.get_broker_services()
    listen = listener('ubox', broker, services)
    listen.connect()
    listen.subscribe()
    listen.loop()

