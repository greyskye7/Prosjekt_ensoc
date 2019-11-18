import threading
import time # Sleep funksjonen tilgjengelig
import socket
import serial
import smbus # Bibliotek for bruk av I2C i Python
import numpy as np # Bibliotek for numpy matriser
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response
import io
import cv2


#For å fjerne advarsler i begynnelsen av programmet
GPIO.setwarnings(False)
#Setter pin-assignment
GPIO.setmode(GPIO.BCM)
#Definerer GPIO 17 som en utgang
GPIO.setup(17, GPIO.OUT)

#Flask server
app = Flask(__name__)
 

#Nunchuck
bus = smbus.SMBus(1) # Oppretter et I2C program grensesnitt med I2C enheten /dev/i2c-1
address = 0x52 # Adressen til slave enheten
bus.write_byte_data(address, 0x40, 0x00) 
bus.write_byte_data(address, 0xF0, 0x55) 
bus.write_byte_data(address, 0xFB, 0x00) 


#UDP for sende og motta data fra C#
# IP-adressen som skal motta udp data i C# 
UDP_IP = "10.0.0.2"
# UDP porten som sender og mottar udp data i C#
UDP_PORT = 9050
# Oppretter en socket som gjør det mulig å sende udp pakker
sock = socket.socket(socket.AF_INET,    
                     socket.SOCK_DGRAM)
# IP-adressen til pi'en. Denne skal motta udp data fra C#
sock.bind(("10.0.0.87", UDP_PORT))

#UDP for node-red
# IP-adressen til pi'en. Denne den skal sende
#udp data til mail via node-red
UDP_IP1 = "10.0.0.87"
# UDP porten som sender udp data til node-red
UDP_PORT1 = 9051



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


def Csharp(): # Funksjon for data som sendes til og fra C#
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
                SerialIOmbed.write("1\n") #Kjører stepper1 til venstre
            elif(kontroll[2] == "1"):
                SerialIOmbed.write("2\n") #Kjører stepper1 til høyre
            elif(kontroll[3] == "1"):
                SerialIOmbed.write("3\n") #Kjører stepper2 oppver
            elif(kontroll[4] == "1"):
                SerialIOmbed.write("4\n") #Kjører stepper2 nedover
            else:
                SerialIOmbed.write("0\n") #Stepper motorene står i ro
            
        

def I2C(): # Funksjon for Nunchuck/I2C
    global manually
    global alarm
    while True:     
        bus.write_byte(address, 0x00) # Disse byte'ene sendes til bus konfigurasjonen for å starte en ny avlesning av Nunchucken
        time.sleep(0.1)
        data0 = bus.read_byte(address) # data0 = adresse 0x00 på busen
        data1 = bus.read_byte(address)
        data2 = bus.read_byte(address)
        data3 = bus.read_byte(address)
        data4 = bus.read_byte(address)
        data5 = bus.read_byte(address)
        data = [data0, data1, data2, data3, data4, data5]
        joy_x = data[0] #data0 er på 1 byte
        joy_y = data[1] #data1 er på 1 byte
        Z_button = (data[5] & 0x01) # Benyttet 1 bit av data5
        
        if(manually == 0): # Betingelse for å kjøre stepper motorene fra Nunchuck
              
            if(joy_x < 134): # Midtverdi for nunchuck i x-akse er 139
                SerialIOmbed.write("1\n") #Er verdien på nunchuck mindre enn 134 i x-akse så kjører stepper1 til venstre
            elif(joy_x > 144):
                SerialIOmbed.write("2\n") #Kjører stepper1 til høyre
            elif(joy_y < 134):
                SerialIOmbed.write("3\n") #Kjører stepper2 oppover
            elif(joy_y > 144):
                SerialIOmbed.write("4\n") #Kjører stepper2 nedover
            else:
                SerialIOmbed.write("0\n") # Stepper motorene står i ro
                
        #Reaktiverer bevegelsesdeteksjon/skrur av
        #alarm med Nunchuck Z-button
        if(alarm == 1): # Hvis alarmen er aktivert
            if(Z_button == 0): # Da kan man med Z knapp på Nunchuck deaktivere alarmen
                print("Alarm deaktivert")
                alarm = 0 #Når alarmen er deaktivert blir denne verdien
                # sendt til C# slik at kontrollpanelet der også blir oppdatert.
                # Denne verdien blir sendt som en UDP melding
                sock.sendto(str(alarm), (UDP_IP, UDP_PORT))


def BLE(): # Funksjon for blåtann-enheten
    global alarm
    while True:
        liste = [0,0,0,0] #Liste for å ta imot data fra BLE
        for i in range(0,3): # En for løkke med fire iterasjoner 
            liste[i] = SerialBLE.read() #Leser data fra blåtann enheten. Dataen blir sendt over seriellporten og lagres en en array.
        blue = liste[0] # Man er kun intressert i det første elementet i array'en
        if(blue == "1"):
            alarm = 0 # Skrur av alarm
            print("Alarm deaktivert")
            # Når alarmen blir deaktivert, brukes den globale variabelen alarm til å oppdatere alarm status i C#, hvor denne dataen blir sendt som en UDP melding.
            sock.sendto(str(alarm), (UDP_IP, UDP_PORT))
        if(blue == "L"):
            SerialIOmbed.write("1\n") #Kjører motor1 mot venstre
        elif(blue == "R"):
            SerialIOmbed.write("2\n") #Kjører motor1 mot høyre
        elif(blue == "U"):
            SerialIOmbed.write("3\n") #Kjører motor2 oppover
        elif(blue == "D"):
            SerialIOmbed.write("4\n") #Kjører motor2 nedover
        else:
            SerialIOmbed.write("0\n") # Begge stepper motorene står i ro




       
    
thread1 = threading.Thread(target=Csharp) # Opprettes en tråd som skal utføre det funksjonen Csharp inneholder
thread1.start() # Starter tråd 1
thread2 = threading.Thread(target=I2C) # Opprettes en tråd som skal utføre det funksjonen I2C inneholder
thread2.start()
thread3 = threading.Thread(target=BLE) # Opprettes en tråd som skal utføre det funksjonen BLE inneholder
thread3.start()



@app.route('/')
def index():
    """Video streaming home page"""
    return render_template('index.html')

def gen():
    global alarm
    vc = cv2.VideoCapture(0) # Oppretter en variabel for 'fange' bilde
    fgbg = cv2.createBackgroundSubtractorMOG2(50,200,True) #???
    frameCount = 0 # Oppretter en teller for å holde kontroll på antall bilder
    
    """Video streaming generator function"""
    while True:
        # Variabel for å lese video feeden som kommer over
        #serieporten fra USB kameraet
        ret, frame = vc.read() 


        frameCount += 1 # Teller øker med en

        #Get the foreground mask
        fgmask = fgbg.apply(frame) #???

        #Count all the nonzero pixels within the mask
        count = np.count_nonzero(fgmask) # Det stillestående i bildet vises som sorte piksler og bevegelse i bildet vises som hvite piksler
        cv2.imwrite('pic.jpg', frame) # Skriver dataen i bildet 'frame' til en jpg fil
        yield(b'--frame\r\n' # ???
                b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')
        
              
        if(alarm == 0): # Alarmen er i bevegelsesdeteksjonsmodus
            if(frameCount > 1 and count > 4500): # Betingelse for å utløse alarm
                print("ALARM!!!!")
                alarm = 1

                # Hvis alarmen utløses så oppdateres alarmstatus
                #verdien i C#, denne verdien sendes som udp-melding
                sock.sendto(str(alarm), (UDP_IP, UDP_PORT))
                
                time.sleep(0.1)

                # Oppretter en socket som gjør det mulig å sende udp pakker
                sock1 = socket.socket(socket.AF_INET,    # Internet protocol
                     socket.SOCK_DGRAM) # User Datagram (UDP)

                # Hvis alarmen utløses, vil det sendes et bilde til
                # en email via node-red. Bildet som sendes til mail,
                # hentes fra samme mappe som python scriptet ligger.
                sock1.sendto(str(frame[1*46080:2*46080]), (UDP_IP1, UDP_PORT1)) 
               
    
                
        

        
        
        
# Opprettes en tråd som skal utføre det funksjonen gen() inneholder
thread4 = threading.Thread(target=gen) 
thread4.start()
                
@app.route('/video_feed') #???
def video_feed():
    return Response(gen(), #???
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__': #???
    app.run(host='10.0.0.87', port=5000,  threaded=True)
   














    














   







 
 

