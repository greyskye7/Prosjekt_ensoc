import smbus
import time
import serial
import RPi.GPIO as GPIO
import socket
from flask import Flask, render_template, Response
from waitress import serve
import cv2
import socket 
import io
import threading

##UDP_IP = "0.0.0.0"
##UDP_PORT = 9050
##sock = socket.socket(socket.AF_INET,    # Internet protocol
##                     socket.SOCK_DGRAM) # User Datagram (UDP)
##sock.bind((UDP_IP, UDP_PORT))
##time.sleep(0.1)



portbt = "/dev/ttyACM1"
Serialbt = serial.Serial(portbt,115200) #setup the serial port and baudrate
Serialbt.flushInput()
Serialbt.flushOutput()#Remove old input's
b=0
c=0
d=0
while True:
    global b                #skal lagre til global variabel
    global c
    global d
    b1=[0,0,0,0]                  #deklarerer en liste for aa ta imot data fra blaatann serielt
    for x in range(0,3):        # for hvert trykk i appen kommer det fire symboler aa ta imot        
        b1[x]=Serialbt.read()   #leser inn ila 4 iterasjoner
    b=b1[1]                     #lagrer kun data vi er interresert i
    c=b1[0]
    print "b0:",b1[0]            #print for debugging
    #print "b1:",b1[1]
    #print "b2:",b1[2]
    #print "b3:",b1[3]
    if(d == 0):
        Serialbt.write("2")
    
    
   
