import socket
import time
import threading
import serial
import smbus
import sys
import numpy as np
import io
import cv2
import pyzbar.pyzbar as pyzbar



#app = Flask(__name__)
vc = cv2.VideoCapture(1)

UDP_IP = "10.0.0.87"
UDP_PORT = 9020
 
print "UDP target IP:",   UDP_IP
print "UDP target port:", UDP_PORT

ret, frame = vc.read()
if ret:
    cv2.imshow("Bilde", frame)
    cv2.imwrite('pic.jpg', frame)
    cv2.waitKey(0)
    


sock = socket.socket(socket.AF_INET,     # Internet protocol
                     socket.SOCK_DGRAM)  # User Datagram (UDP)


#d = frame.flatten ()
s = frame.tostring ()



#Make a csv string 
#Message="A"*9217


# Send the csv string as a UDP message
sock.sendto(s[1*46080:2*46080], (UDP_IP, UDP_PORT))

vc.release()
cv2.destroyAllWindows()







    

