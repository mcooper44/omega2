from datetime import datetime, date
import time
import json

import paho.mqtt.client as mqtt

from mqtt_config import configuration
from mqtt_database import mqtt_database

MQTT_DB = mqtt_database()

def log_to_db(database, sid, temp):
    '''
    passes the payload to the db for storage
    '''
    log_time = datetime.now()
    database.insert_value((sid, temp, log_time))

def on_message(client, userdata, message):
    time.sleep(1)
    json_payload = str(message.payload.decode("utf-8"))
    payload = json.loads(json_payload)
    sensor = payload['sensor']
    reading = payload['reading']
    print(f'{sensor} said: {reading}')
    log_to_db(MQTT_DB, sensor, reading)

def on_publish(client, userdata, mid):
    print('message ID: {}'.format(mid))
        
def main(client_name, broker, services):
    
    client = mqtt.Client(client_name)
    client.on_message = on_message
    client.on_publish = on_publish
    broker = broker
    services = services

    '''
    Connect to the broker so that we can subscribe 
    and start recieving messages
    '''
    client.connect(broker)
    print(f'connected to broker: {broker}')
    time.sleep(2)

    '''
    subscribe to the services in the list
    passed into the object when it was 
    instantiated 
    '''
    for service in services:
        client.subscribe(service)
        print(f'subscribed to {service}')
        time.sleep(4)

    '''
    listen to the broker
    and recieve payloads from the services 
    that the listener connected to by invoking the 
    subscribe method
    Requires that a call to connect and subscribe
    to be previously called
    '''
    try:
        while True:
            print('beginning loop')
            client.loop_forever()
    except (EOFError, KeyboardInterrupt) as e:
        print('{}  <- this happened'.format(e))
        client.loop_stop()
        client.disconnect()
        MQTT_DB.close_connection()

if __name__ == '__main__':
    conf = configuration('config.yaml')
    DB = 'swarm_log.sqlite3'
    broker, services = conf.get_broker_services()
    client_name = conf.c_name
    print(f'{client_name} is attempting to listen to {broker} for {services}')
    main(client_name, broker, services)
    
