import threading
import time
import socket
import serial
import smbus
#import sys
import numpy as np
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response
import io
import cv2
#import pyzbar.pyzbar as pyzbar

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM) 
GPIO.setup(17, GPIO.OUT)

#Flask server
app = Flask(__name__)
 

#Nunchuck
bus = smbus.SMBus(1)
address = 0x52
bus.write_byte_data(address, 0x40, 0x00)
bus.write_byte_data(address, 0xF0, 0x55)
bus.write_byte_data(address, 0xFB, 0x00)

#UDP for sende fra C#
UDP_IP = "10.0.0.2"
UDP_PORT = 9010
sock = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)
sock.bind(("10.0.0.87", UDP_PORT))

#UDP for node-red
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



manually = 0 #Manuell kontroll
alarm = 0 #Alarm status


def loop1():
    global manually
    global alarm
    
    while True:
        data, addr = sock.recvfrom(1280) # Max recieve size is 1280 bytes
        kontroll = data.split(",")
       
        if(kontroll[6] == "1"): #Styres fra C#
            manually = 1
        if(kontroll[6] == "0"): #Styres fra Nunchuck
            manually = 0
        if(kontroll[5] == "1"): #Alarm På,
            alarm = 1
            GPIO.output(17, GPIO.HIGH)
        if(kontroll[5] == "0"): #Alarm av
            alarm = 0
            GPIO.output(17, GPIO.LOW)
            
        
        if(manually == 1):
            if(kontroll[1] == "1"):
                SerialIOmbed.write("1\n") #Kjører stepper til venstre
            elif(kontroll[2] == "1"):
                SerialIOmbed.write("2\n") #Kjører stepper til høyre
            elif(kontroll[3] == "1"):
                SerialIOmbed.write("3\n") #Kjører stepper til opp
            elif(kontroll[4] == "1"):
                SerialIOmbed.write("4\n") #Kjører stepper til ned
            else:
                SerialIOmbed.write("0\n")
            
        

def loop2():
    global manually
    global alarm
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
        
        if(manually == 0):
              
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
        #Reaktiverer bevegelsesdeteksjon/skrur av
        #alarm med Nunchuck Z-button
        if(alarm == 1):
            if(Z_button == 0):
                print("Alarm deaktivert")
                alarm = 0
                sock.sendto(str(alarm), (UDP_IP, UDP_PORT))


def loop3():
    global alarm
    while True:
        liste = [0,0,0,0] #Liste for å ta imot data fra BLE
        for i in range(0,3):
            liste[i] = SerialBLE.read()
        blue = liste[0]
        if(blue == "1"):
            alarm = 0 # Skrur av alarm/på med bevegelsesdeteksjon
            print("Alarm deaktivert")
            sock.sendto(str(alarm), (UDP_IP, UDP_PORT))
        if(blue == "L"):
            SerialIOmbed.write("1\n") #Kjører motor mot venstre
        elif(blue == "R"):
            SerialIOmbed.write("2\n")
        elif(blue == "U"):
            SerialIOmbed.write("3\n")
        elif(blue == "D"):
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
    global alarm
    vc = cv2.VideoCapture(0) 
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
        
              
        if(alarm == 0):
            if(frameCount > 1 and count > 4500): 
                print("ALARM!!!!")
                alarm = 1
                sock.sendto(str(alarm), (UDP_IP, UDP_PORT))
                time.sleep(0.1)
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
   














    














   







 
 

