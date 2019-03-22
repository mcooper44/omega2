import os
import subprocess
import time

# specify delay duration to be used in the program
setupDelay = 3

# variables to hold filesystem paths
oneWireDir = "/sys/devices/w1_bus_master1"
paths = {
    "slaveCount": oneWireDir + "/w1_master_slave_count",
    "slaves": oneWireDir + "/w1_master_slaves"        
}

## a bunch of functions to be used by the OneWire class
# insert the 1-Wire kernel module
# it's also called a "module", but it's actually software for the Omega's firmware!
# https://docs.onion.io/omega2-docs/communicating-with-1w-devices.html
def insertKernelModule(gpio):
    '''
    uses the insmod command to insert the custom kernel module
    for using 1 wire devices with the omega2.
    
    use the removeKernelModule(gpio) function to remove the module
    and free up resources
    
    more material on the kernel module is found at:
    https://github.com/OnionIoT/source/blob/openwrt-18.06/package/kernel/w1-gpio-custom/src/w1-gpio-custom.c
    '''
    argBus = "bus0=0," + gpio + ",0"
    subprocess.call(["insmod", "w1-gpio-custom", argBus])

# check the filesystem to see if 1-Wire is properly setup
def checkFilesystem():
    '''
    the module will create a directory in the /sys/devices/ folder
    called w1_bus_master1.   using the os module this function
    will return true of false indicating if the kernel module was 
    inserted sucessfully or not
    '''
    return os.path.isdir(oneWireDir)

# function to setup the 1-Wire bus
def setupOneWire(gpio, times_to_try=2):
    '''
    uses the checkFilesystem function to determine if the 
    oneWire directory has been setup as a result of inserting 
    the kernel module
    '''
    # check and retry up to n times if the 1-Wire bus has not been set up
    for i in range (times_to_try):
	
        if checkFilesystem():
            return True # exits if the bus is setup

        # tries to insert the module if it's not setup
        insertKernelModule(gpio)
        # wait for a bit, then check again
        time.sleep(setupDelay)
    else:
        # could not set up 1-Wire on the gpio
        return False

# check that the kernel is detecting slaves
def checkSlaves():
    with open(paths["slaveCount"]) as slaveCountFile:
        slaveCount = slaveCountFile.read().split("\n")[0]

    if slaveCount == "0":
        # slaves not detected by kernel
        return False
    return True

# check if a given address is registered on the bus
def checkRegistered(address):
    slaveList = scanAddresses()
    registered = False
    for line in slaveList:
        if address in line:
            registered = True
    return registered

# scan addresses of all connected 1-w devices
def scanAddresses():
    '''
    the omega kernal module will mount the hardware to a dir
    with the name of the attached one wire device
    the kernel module scans for attached devices at a regular interval
    
    param: label can be invoked if using this method to 
    identify the serial number of the device for labelling purposes
    it should be the type of hardware i.e. ds18b20 etc.
    '''
    if not checkFilesystem():
        return False

    with open(paths["slaves"]) as slaveListFile:
        slaveList = slaveListFile.read().split("\n")
        # last element is an empty string due to the split
        del slaveList[-1]
    return slaveList

# use to get the address of a single connected device
def scanOneAddress():
    '''
    returns the address of the first device in the directory listing
    of attached one wire devices
    '''
    addresses = scanAddresses()
    return addresses[0]

# class definition for one wire devices
class OneWire:
    def __init__(self, address, gpio=19):      # use gpio 19 by default if not specified
        self.gpio = str(gpio)
        self.address = str(address)
        self.slaveFilePath = oneWireDir + "/" + self.address + "/" + "w1_slave"
        self.setupComplete = self.__prepare()

    # prepare the object
    def __prepare(self):
        # check if the system file exists
        # if not, set it up, then check one more time
	# store return value True/False in self.setupComplete
        if not setupOneWire(self.gpio):
            print("Could not set up 1-Wire on GPIO " + self.gpio)
            return False

        # check if the kernel is recognizing slaves
        if not checkSlaves():
            print("Kernel is not recognizing slaves.")
            return False

        # check if this instance's device is properly registered
        if not checkRegistered(self.address):
            # device is not recognized by the kernel
            print("Device is not registered on the bus.")
            return False                        

        # the device has been properly set up
        return True

    # function to read data from the sensor
    def readDevice(self):
        # read from the system file
        with open(self.slaveFilePath) as slave:
            message = slave.read().split("\n")
            # return an array of each line printed to the terminal
        return message