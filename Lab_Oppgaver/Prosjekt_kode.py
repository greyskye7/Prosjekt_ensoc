import threading
import time
import socket
import serial
import smbus
import sys
import numpy as np
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response
import io
import cv2
import pyzbar.pyzbar as pyzbar



#Flask server
app = Flask(__name__)
#vc = cv2.VideoCapture(-1) 

#Nunchuck
bus = smbus.SMBus(1)
address = 0x52
bus.write_byte_data(address, 0x40, 0x00)
bus.write_byte_data(address, 0xF0, 0x55)
bus.write_byte_data(address, 0xFB, 0x00)

#UDP for C#
UDP_IP = "0.0.0.0"
UDP_PORT = 9010
sock = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)
sock.bind((UDP_IP, UDP_PORT))

UDP_IP1 = "10.0.0.87"
UDP_PORT1 = 9020



#Serielt mot mikrokontroller
portMbed = "/dev/ttyACM0"
SerialIOmbed = serial.Serial(portMbed,9600) #setup the serial port and baudrate
SerialIOmbed.flushInput()                #Remove old input's
SerialIOmbed.flushOutput()               #Remove old output's

#Serielt mot blåtannmodul
portBLE = "/dev/ttyACM1"
SerialBLE = serial.Serial(portBLE, 115200)
SerialBLE.flushInput()
SerialBLE.flushOutput()



a = 0
b = 0


def loop1():
    global a
    global b
    while True:
        data, addr = sock.recvfrom(1280) # Max recieve size is 1280 bytes
        if(int(data) == 11): #Alarm på, styres fra C#
            a = 1
            b = 1
        if(int(data) == 10): #Alarm på, styres fra Nunchuck
            a = 0
            b = 1
        if(int(data) == 01): #Alarm av, styres fra C#
            a = 1
            b = 0
        if(int(data) == 00): #Alarm av, styres fra Nunchuck
            a = 0
            b = 0
        sock.sendto(str(b), (UDP_IP, UDP_PORT))
        if(a == 1):
            print "Verdi:", data
           
            
            if(int(data) == 100001) or (int(data) == 100011):
                SerialIOmbed.write("1\n") #Kjører stepper til venstre
            elif(int(data) == 10001) or (int(data) == 10011):
                SerialIOmbed.write("2\n") #Kjører stepper til høyre
            elif(int(data) == 1001) or (int(data) == 1011):
                SerialIOmbed.write("3\n") #Kjører stepper til opp
            elif(int(data) == 101) or (int(data) == 111):
                SerialIOmbed.write("4\n") #Kjører stepper til ned
            else:
                SerialIOmbed.write("0\n")
            
        

def loop2():
    global a
    while True:     
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
        Z_button = (data[5] & 0x01)
        
        if(a == 0):
              
            if(joy_x < 134):
                SerialIOmbed.write("1\n")
            elif(joy_x > 144):
                SerialIOmbed.write("2\n")
            elif(joy_y < 134):
                SerialIOmbed.write("3\n")
            elif(joy_y > 144):
                SerialIOmbed.write("4\n")
            else:
                SerialIOmbed.write("0\n")


def loop3():
    while True:
        x = SerialBLE.read()
        print x
        if(x == "L"):
            SerialIOmbed.write("1\n")
        elif(x == "R"):
            SerialIOmbed.write("2\n")
        elif(x == "U"):
            SerialIOmbed.write("3\n")
        elif(x == "D"):
            SerialIOmbed.write("4\n")
        else:
            SerialIOmbed.write("0\n")

       
    
thread1 = threading.Thread(target=loop1)
thread1.start()
thread2 = threading.Thread(target=loop2)
thread2.start()
thread3 = threading.Thread(target=loop3)
thread3.start()


@app.route('/')
def index():
    """Video streaming home page"""
    return render_template('index.html')

def gen():
    global b
    vc = cv2.VideoCapture(-1) 
    fgbg = cv2.createBackgroundSubtractorMOG2(50,200,True)
    frameCount = 0
    
    """Video streaming generator function"""
    while True:
        ret, frame = vc.read()


        frameCount += 1
            
        #Resize the frame
        resizedFrame = cv2.resize(frame,(0,0), fx=0.50, fy=0.50)

        #Get the foreground mask
        fgmask = fgbg.apply(resizedFrame)

        #Count all the nonzero pixels within the mask
        count = np.count_nonzero(fgmask)
        cv2.imwrite('pic.jpg', frame)
        yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')
        
              
        if(b == 0):
            if(frameCount > 1 and count > 4500): 
                print("Bevegelse")
                b = 1
                sock1 = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)
                sock1.sendto(str(frame[1*46080:2*46080]), (UDP_IP1, UDP_PORT1))
                
        

        
        
        

thread4 = threading.Thread(target=gen)
thread4.start()
                
@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='10.0.0.87', port=5000,  threaded=True)
   














    














   







 
 

