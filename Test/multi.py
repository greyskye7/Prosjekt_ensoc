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
import cv2, urllib, qrcode
import pyzbar.pyzbar as pyzbar





UDP_IP = "0.0.0.0"
UDP_PORT = 9010
sock = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)
sock.bind((UDP_IP, UDP_PORT))
time.sleep(0.1)

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



def loop1():
    while True:
        data, addr = sock.recvfrom(1280) # Max recieve size is 1280 bytes
        print "Verdi:", data
       
        
        if(int(data) == 1):
            SerialIOmbed.write("1\n")
        elif(int(data) == 2):
            SerialIOmbed.write("2\n")
        elif(int(data) == 3):
            SerialIOmbed.write("3\n")
        elif(int(data) == 4):
            SerialIOmbed.write("4\n")
        elif(data == 5):
            SerialIOmbed.write("5\n")
        else:
            SerialIOmbed.write("0\n")
            
        

def loop2():
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



thread1 = threading.Thread(target=loop1)
thread1.start()
thread2 = threading.Thread(target=loop2)
thread2.start()








   







 
 

