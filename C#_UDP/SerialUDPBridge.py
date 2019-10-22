import serial #Serial port API http://pyserial.sourceforge.net/pyserial_api.html
import socket
import time
from threading import Thread


def recvUDP(sock,SerialIOArduino):
    while True:
        data, addr = sock.recvfrom(1280) # Max recieve size is 1280 bytes
       # print "UDP received message:", data.strip()
        SerialIOArduino.write(data)
    

port = "/dev/ttyACM0"

UDP_IP = "10.0.0.2"
UDP_PORT = 9030
 
print "UDP target IP:",   UDP_IP
print "UDP target port:", UDP_PORT

sock = socket.socket(socket.AF_INET,     # Internet protocol
                     socket.SOCK_DGRAM)  # User Datagram (UDP)
sock.bind(("0.0.0.0", UDP_PORT))           # Listen on all adapters

SerialIOArduino = serial.Serial(port,9600) # setup the serial port and baudrate
SerialIOArduino.flushInput() # Remove old input's
SerialIOArduino.flushOutput() 

t = Thread(target=recvUDP,args=(sock,SerialIOArduino,))
t.daemon=True # Stop thread when program ends
t.start()

while True:
    if (SerialIOArduino.inWaiting() > 0):
        inputLine = SerialIOArduino.readline().strip()  # read a '\n' terminated line()

        # Send the csv string as a UDP message
        sock.sendto(inputLine, (UDP_IP, UDP_PORT))
    
