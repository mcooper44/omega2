from datetime import datetime, date
import time
import sqlite3
import paho.mqtt.client as mqtt
from mqtt_config import configuration

INIT_STRING = """CREATE TABLE IF NOT EXISTS TempData (ID text, 
temp real NOT NULL, date date NOT NULL)"""
INSERT_STRING = "INSERT INTO TempData (ID, temp, date) VALUES (?, ?, ?)"
FETCH_STRING = "SELECT from TempData WHERE ID=?"
DB = None

class mqtt_database():
    def __init__(self, path):
        self.path = path
        self.con = None
        self.cursor = None
        try:
            self.con = sqlite3.connect(self.path)
            self.cursor = self.con.cursor()
            self.cursor.execute(INIT_STRING)
            self.con.commit()
        except Exception as dbase_error:
            print(dbase_error)

    def insert_value(self, payload):
        '''
        accepts a tuple and inserts it into the database
        '''
        self.cursor.execute(INSERT_STRING, payload)
        self.con.commit()
    
    def fetch_value(self, r_value):
        '''
        param: r_value = tuple of strings to extract from 
        the database
        '''
        self.cursor.execute(FETCH_STRING, r_value)
        return self.cursor.fetchall()
    
    def shut_connection(self):
        self.con.close()
        
class listener():
    def __init__(self, client_name, broker, services):
        self.client = mqtt.Client(client_name)
        self.broker = broker
        self.services = services
        self.ok_go = True
	
        if self.client:
            self.client.on_message = listener.on_message
            self.client.on_publish = listener.on_publish
    
    @staticmethod
    def log_to_db(self, database, payload):
        '''
	    passes the payload to the db for storage
	    '''
        log_time = datetime.now()
        sid, temp = payload

        database.insert_value((sid, temp, log_time))
    
    @staticmethod
    def on_message(self, client, userdata, message):
        time.sleep(1)
        payload = str(message.payload.decode("utf-8"))
        print('{}'.format(payload))
        listener.log_to_db(DB, payload)
	
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
    DB = mqtt_database('swarm_log.sqlite3')
    conf = configuration('config.yaml')
    broker, services = conf.get_broker_services()
    listen = listener('ubox', broker, services)
    listen.connect()
    listen.subscribe()
    listen.loop()

