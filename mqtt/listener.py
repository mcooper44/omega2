import time
import paho.mqtt.client as mqtt
import yaml

class configuration():
    def __init__(self, config_file):
        self.config_file = config_file
        self.broker = None
        self.broker_name = None
        self.service_list = None

        if self.config_file:
            try:
                with open(config_file, 'r') as ymlfile:
                    yfile = yaml.load(ymlfile)
                    self.broker = yfile['server']['broker']
                    print('Broker: {}'.format(self.broker))
                    self.broker_name = yfile['server']['server_type']

                    self.service_list = yfile['service']['targets']
                    print('Services: {}'.format(self.service_list))
            except:
                print('failed to open config file')

    def get_broker_services(self):
        return self.broker, self.service_list

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
    def on_message(client, userdata, message):
        time.sleep(1)
        payload = str(message.payload.decode("utf-8"))
        print('{}'.format(payload))

    @staticmethod
    def on_publish(client, userdata, mid):
        print('message ID: {}'.format(mid))

    def connect(self):
        self.client.connect(self.broker)

    def subscribe(self):
        for service in self.services:
            self.client.subscribe(service)

    def loop(self):
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

