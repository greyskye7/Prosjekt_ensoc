#Install the serial library first
# sudo apt-get install python-serial
import serial #Serial port API http://pyserial.sourceforge.net/pyserial_api.html
import time
import smbus #Enables the python bindings for I2C

port = "/dev/ttyACM0"
bus = smbus.SMBus(1)
address = 0x52
bus.write_byte_data(address, 0x40, 0x00)
bus.write_byte_data(address, 0xF0, 0x55)
bus.write_byte_data(address, 0xFB, 0x00)
time.sleep(0.1)

SerialIOmbed = serial.Serial(port,9600) #setup the serial port and baudrate
SerialIOmbed.flushInput()                #Remove old input's
SerialIOmbed.flushOutput()
while True:
    try:
        bus.write_byte(address, 0x00)
        time.sleep(0.1)
        data0 = bus.read_byte(address)
        data1 = bus.read_byte(address)
        data2 = bus.read_byte(address)
        data3 = bus.read_byte(address)
        data4 = bus.read_byte(address)
        data5 = bus.read_byte(address)
        data = [data0, data1, data2, data3, data4, data5]
        joy_x = data[0]
        if(joy_x < 139):
            SerialIOmbed.write("-1\n")
        elif(joy_x == 139):
            SerialIOmbed.write("0\n")
        else:
            SerialIOmbed.write("1\n")
    except IOError as e:
        print e

