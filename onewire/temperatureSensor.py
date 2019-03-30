from oneWire import OneWire

class onewire_temp_sensor:
    def __init__(self, address, gpio):
        self.address = address
        self.gpio = gpio
        self.last_reading = None
        self.ready_status = False
        self.driver = None

        if all((self.address, self.gpio)):
            self.driver = OneWire(self.address, self.gpio)

        if self.driver:
            self.ready_status = self.driver.setupComplete
    
    def get_status(self):
        return self.ready_status

    def read_temp(self):
        try:
            # device typically prints 2 lines, the 2nd line has the temperature sensor at the end
            # eg. a6 01 4b 46 7f ff 0c 10 5c t=26375
            rawValue = self.driver.readDevice()
            # grab the 2nd line, then read the last entry in the line, then get everything after the "=" sign
            value = rawValue[1].split()[-1].split("=")[1]
            # convert value from string to number
            value = int(value)
            # DS18B20 outputs in 1/1000ths of a degree C, so convert to standard units
            value /= 1000.0
            self.last_reading = value
            return value
        except Exception as error:
            print('could not read from {} at pin {}'.format(self.address, self.gpio))
            print('Ready Status is {} and last reading was {}'.format(self.ready_status,
                                                                      self.last_reading))
            print('returned error {}'.format(error))
            return False

# main class definition
class TemperatureSensor:
    '''
    a controller class for temperature sensors
    '''

    def __init__(self):
        self.supportedInterfaces = ["oneWire"]
        self.ready = False
        self.sensors = {}

    def add_supported_type(self, s_type):
        '''
        adds a string s_type to supportedInterfaces
        '''
        self.supportedInterfaces.append(s_type)
    
    def listInterfaces(self):
        print("The supported interfaces are:")
        for interface in self.supportedInterfaces:
            print(interface)

    def add_sensor(self, interface, args):
        '''
        adds a sensor with a specific interface type
        args provided depend on class of sensor
        '''

        # if specified interface not supported
        if interface not in self.supportedInterfaces:
            print("Unsupported interface.")
            self.listInterfaces()
            return

        # set up a driver based on the interface type
        # you can extend this class by adding more drivers! (eg. serial, I2C, etc)
        if interface == "oneWire":
            '''
            requires address: string
                     gpio: pin number as int
            '''
            sensor = onewire_temp_sensor(args.get("address", None), args.get("gpio", None))
            # signal ready status
            sensor_ready = sensor.get_status()
            if sensor_ready:
                s_id = args.get('address', None)
                self.sensors[s_id] = sensor
            else:
                print('Could not attach sensor.')
                return
    
    def read_sensor(self, address):
        try:
            if self.sensors.get(address, False).get_status():
                return self.sensors.get(address, False).read_temp()
            else:
                return False
        except:
            print('could not read sensor')

    def ask_status(self, address):
        return self.sensors.get(address, False).get_status()