import json

class configuration():
    '''
    This class loads a json configuration file
    refer to the yaml_template file for info on structure
    
    '''
    def __init__(self, config_file):
        self.config_file = config_file
        self.broker = None
        self.broker_name = None
        self.service_list = None # master list
        self.device_profile = None # master list in dict form keys = dev_name
        self.c_name = None 
        self.c_devices = None # client specific list
        self.c_services = None # client specific list of device names i.e. dev_id_1
	
        if self.config_file:
            try:
                with open(config_file, 'r') as ymlfile:
                    yfile = json.load(ymlfile)
                    self.broker = yfile['server']['broker']
                    print('Broker: {}'.format(self.broker))
                    self.broker_name = yfile['server']['server_type']

                    self.service_list = yfile['service']['targets'] # list of paths a/b/c
                    print('Services loaded: {}'.format(self.service_list))
		    
                    self.device_profile = yfile['devices'] # device dictionaries
                    print('Devices : {}'.format(self.device_profile))
		            
                    self.c_name = yfile['client']['client_name']
                    self.c_devices = yfile['client']['devices'] # names dev_id_1
                    print('client name {} with devices {}'.format(self.c_name, self.c_devices))
            except:
                print('failed to open config file')

    def get_broker_services(self):
        return self.broker, self.service_list
	
    def get_client(self):
        '''
        returns a tuple of broker and client name
        '''
        return self.broker, self.c_name
	
    def get_device_profile(self, dev_name):
        '''
        returns a dictionary of 
        service: a/b/c
        type: of device
        returns: a single value or [list of what it returns temp, humidity etc]
        location: str of where the device is
        interval: int of how often it should be pinged and return a reading
        '''
        return self.device_profile.get(dev_name, None)
    
    def get_device_by_type(self, dev_type):
	    devices = []
	    for dev in self.device_profile.keys():
		    if self.device_profile[dev]['type'].get(dev_type, None):
			    devices.append(self.device_profile[dev])
	    return devices