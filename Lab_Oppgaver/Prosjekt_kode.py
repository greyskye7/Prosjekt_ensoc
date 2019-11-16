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
bus = smbus.SMBus(1) # Oppretter et I2C program grensesnitt med I2C enheten /dev/i2c-1
address = 0x52 # Adressen til slave enheten
bus.write_byte_data(address, 0x40, 0x00) # Bruker I2C adressen til å sende kommandoen 0x40 med dataen 0x00
bus.write_byte_data(address, 0xF0, 0x55) # Bruker I2C adressen til å sende kommandoen 0xF0 med dataen 0x55
bus.write_byte_data(address, 0xFB, 0x00) # Bruker I2C adressen til å sende kommandoen 0xFB med dataen 0x00
# FINNE UT HVA KOMMANDOENE I write_byte_data gjør!!!!!
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
portMbed = "/dev/ttyACM0" #Deklarerer en variabel for en serieport
SerialIOmbed = serial.Serial(portMbed,9600) #Setter opp et serieport objekt med definert overføringshastighet 
SerialIOmbed.flushInput()  #Når koden kjøres utføres første gang, fjernes gammel input fra bufferet til serieporten
SerialIOmbed.flushOutput()  #Når koden kjøres utføres første gang, fjernes gammel output fra bufferet til serieporten             



#Serielt mot blåtannmodul
portBLE = "/dev/ttyACM1" #Deklarerer en variabel for en serieport
SerialBLE = serial.Serial(portBLE, 115200) #Setter opp et serieport objekt med definert overføringshastighet
SerialBLE.flushInput() #Når koden kjøres utføres første gang, fjernes gammel input fra bufferet til serieporten
SerialBLE.flushOutput() #Når koden kjøres utføres første gang, fjernes gammel output fra bufferet til serieporten



manually = 0 #Variabel for motorstyring fra Nunchuck eller C#
alarm = 0 #Variabel for alarm status


def Csharp():
    global manually #Ved å gjøre variabelene globale kan funksjonene dele på de samme variabelene. Når en variabel verdi endres så gjør den det alle steder den er inkludert
    global alarm
    
    while True:
        data, addr = sock.recvfrom(1280) #Data overføres fra C# via UDP melding. Maks størrelse på dataen som overføres er 1280 bytes.
        kontroll = data.split(",")#Dataen fra C# sendes som en lang string. Her splittes dataen opp i en array hvor elementene er delt for hver komma. Dette kalles Comma separated values(CSV).
       
        if(kontroll[6] == "1"): # 7 element i array'en i dataen mottatt fra C#.  
            manually = 1 # Settes kontroll[6] høy så er stepper motorene styrt fra C#
        if(kontroll[6] == "0"): 
            manually = 0 # Settes kontroll[6] lav så er stepper motorene styrt med Nunchuck/I2C
        if(kontroll[5] == "1"): # 6 element i array'en i dataen mottatt fra C#. 
            alarm = 1 # Settes kontroll[5] høy så utløses alarmen
            GPIO.output(17, GPIO.HIGH) # GPIO 17, som er satt som en utgang aktiverer en lysdiode som indikerer at alarmen har gått
        if(kontroll[5] == "0"): 
            alarm = 0 # Settes kontroll[5] lav så er alarmen deaktivert
            GPIO.output(17, GPIO.LOW) # GPIO 17 er lav og indikerer at alarmen er av
            
        
        if(manually == 1): # Betingelse for å kjøre stepper motorene fra C#
            if(kontroll[1] == "1"): # 2 element i array'en i dataen mottatt fra C#.
                SerialIOmbed.write("1\n") #Kjører stepper til venstre
            elif(kontroll[2] == "1"):
                SerialIOmbed.write("2\n") #Kjører stepper til høyre
            elif(kontroll[3] == "1"):
                SerialIOmbed.write("3\n") #Kjører stepper til opp
            elif(kontroll[4] == "1"):
                SerialIOmbed.write("4\n") #Kjører stepper til ned
            else:
                SerialIOmbed.write("0\n") #Stepper motorene står i ro
            
        

def I2C():
    global manually
    global alarm
    while True:     
        bus.write_byte(address, 0x00) # Disse byte'ene sendes til bus konfigurasjonen for å starte en ny avlesning av Nunchucken
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


def BLE():
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




       
    
thread1 = threading.Thread(target=Csharp)
thread1.start()
thread2 = threading.Thread(target=I2C)
thread2.start()
thread3 = threading.Thread(target=BLE)
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
   














    














   







 
 

