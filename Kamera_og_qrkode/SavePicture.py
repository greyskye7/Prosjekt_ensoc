import cv2
import numpy as np

cam = cv2.VideoCapture(0)
b,img = cam.read()
if b:
    cv2.imshow("Bilde1", img) #Viser bildet med navn Bilde1
    cv2.imwrite('Picture.jpg',img)#Lagrer bilde som Picture.jpg
    print("Saved picture") #Skriver til skjerm
    cv2.waitKey(0) #Trykk en kanpp for å avslutte

    img2 = cv2.imread('Picture.jpg',0) #Gjør bildet til gråskala
    cv2.imshow("Picture", img2)#Viser bildet i gråskala
    cv2.waitKey(0) #Trykk en kanpp for å avslutte

else:
    print("Kameraet fungerer ikke")
    print("Filen ble ikke lagret")
cam.release()
cv2.destroyAllWindows()
