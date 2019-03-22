import yaml

class configuration():
    '''
    This class loads a yaml configuration file
    refer to the yaml_template file for info on structure
    
    '''
    def __init__(self, config_file):
        self.config_file = config_file
        self.broker = None
        self.broker_name = None
        self.service_list = None # master list
	self.devices = None # master list
	self.c_name = None 
	self.c_devices = None # client specific list
	self.c_services = None # client specific list
	
        if self.config_file:
            try:
                with open(config_file, 'r') as ymlfile:
                    yfile = yaml.load(ymlfile)
                    self.broker = yfile['server']['broker']
                    print('Broker: {}'.format(self.broker))
                    self.broker_name = yfile['server']['server_type']

                    self.service_list = yfile['service']['targets']
                    print('Services loaded: {}'.format(self.service_list))
		    
		    self.devices = yfile['devices']
		    print('Devices : {}'.format(self.devices.keys()))
		    
		    self.c_name = yfile['client']['client_name']
		    self.c_devices = yfile['client']['devices']
                print('failed to open config file')

    def get_broker_services(self):
        return self.broker, self.service_listc
	
    def get_client(self):
	return self.broker, self.c_name
	
    def get_device_profile(self, dev_name):
	    return self.devices.get(dev_name, None)
    
    def get_device_by_type(self, dev_type):
	    devices = []
	    for dev in self.c_devices:
		    if self.devices[dev]['type'].get(dev_type, None):
			    devices.append(self.devices[dev])
	    return devices