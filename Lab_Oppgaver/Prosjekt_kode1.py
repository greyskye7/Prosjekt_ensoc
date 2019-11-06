import threading
import time
import socket
import serial
import smbus
import sys
import numpy as np
import RPi.GPIO as GPIO
from waitress import serve
from flask import Flask, render_template, Response
import io
import cv2
import pyzbar.pyzbar as pyzbar


app = Flask(__name__)
vc = cv2.VideoCapture(-1) #Hadde problemer med index 0,
                    #index(-1) tar i bruk det første tilgjengelige kameraet
fgbg = cv2.createBackgroundSubtractorMOG2(50,200,True)

UDP_IP = "0.0.0.0"
UDP_PORT = 9010
sock = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)
sock.bind((UDP_IP, UDP_PORT))


port = "/dev/ttyACM0"
port2 = "/dev/ttyACM1"
bus = smbus.SMBus(1)
address = 0x52
bus.write_byte_data(address, 0x40, 0x00)
bus.write_byte_data(address, 0xF0, 0x55)
bus.write_byte_data(address, 0xFB, 0x00)



SerialIOmbed = serial.Serial(port,9600) #setup the serial port and baudrate
SerialIOmbed.flushInput()                #Remove old input's
SerialIOmbed.flushOutput()
SerialBLE = serial.Serial(port2, 9600)
SerialBLE.flushInput()
SerialBLE.flushOutput()

b = 0



    

def loop1():
    global b
    if(b == 0):
        frameCount = 0
        while True:  
            ret1, frame1 = vc.read()
            frameCount += 1
            
            #Resize the frame
            resizedFrame = cv2.resize(frame1,(0,0), fx=0.50, fy=0.50)

            #Get the foreground mask
            fgmask = fgbg.apply(resizedFrame)

            #Count all the nonzero pixels within the mask
            count = np.count_nonzero(fgmask)

                

            if(frameCount > 1 and count > 10000):
                
                print("Bevegelse")
                b = 1
                




thread1 = threading.Thread(target=loop1)
thread1.start()

if(b == 1):
    @app.route('/')
    def index():
        """Video streaming home page"""
        return render_template('index.html')

    def gen():
        """Video streaming generator function"""
        while True:
            ret, frame = vc.read()
            cv2.imwrite('pic.jpg', frame)
            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    if __name__ == '__main__':
        #serve(app, host='10.0.0.79', port=5000)
        app.run(host='10.0.0.79', port=5000,  threaded=True)

