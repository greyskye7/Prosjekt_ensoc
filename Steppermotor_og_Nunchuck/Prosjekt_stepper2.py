#Install the serial library first
# sudo apt-get install python-serial
import serial #Serial port API http://pyserial.sourceforge.net/pyserial_api.html
import time
import smbus #Enables the python bindings for I2C
import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 9030
sock = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)
sock.bind((UDP_IP, UDP_PORT))

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

while(True):
    data, addr = sock.recvfrom(1280) # Max recieve size is 1280 bytes
    print "Verdi:", data
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
    joy_y = data[1]

    if(joy_x < 134):
        SerialIOmbed.write("1\n")
    elif(int(data) == 1000):
        SerialIOmbed.write("1\n")
    elif(int(data) == 100):
        SerialIOmbed.write("2\n")
    elif(int(data) == 10):
        SerialIOmbed.write("3\n")
    elif(int(data) == 01):
        SerialIOmbed.write("4\n")
    elif(int(data) == 5):
        break 
    else:
        SerialIOmbed.write("0\n")
