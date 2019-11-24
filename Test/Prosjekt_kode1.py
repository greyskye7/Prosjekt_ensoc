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




UDP_IP = "0.0.0.0"
UDP_PORT = 9010
sock = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)
sock.bind((UDP_IP, UDP_PORT))
while True:
    data, addr = sock.recvfrom(1280) # Max recieve size is 1280 bytes
    data1 = data.split(",")
    for i in range(0,7):
        if(data1[i] == "1"):
            print(i)











    



