#Install the serial library first
# sudo apt-get install python-serial
import serial #Serial port API http://pyserial.sourceforge.net/pyserial_api.html
import smbus #Enables the python bindings for I2C
import time #Enables sleep functions
port = "/dev/ttyACM0"
bus = smbus.SMBus(1)
address = 0x52
bus.write_byte_data(address, 0x40, 0x00)
bus.write_byte_data(address, 0xF0, 0x55)
bus.write_byte_data(address, 0xFB, 0x00)
time.sleep(0.1)



SerialIOmbed = serial.Serial(port,9600) #setup the serial port and baudrate
SerialIOmbed.flushInput() #Remove old input's



while True:
    if (SerialIOmbed.inWaiting() > 0):
        inputLine = SerialIOmbed.readline().strip()  # read a '\n' terminated line()
        comands=inputLine.split(",") # Splits the line into a table/list like : ['$SW', '1', '1', '0', '0']
        print(comands)
        SerialIOmbed.write(100)
        SerialIOmbed.close()

