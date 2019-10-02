import cv2
import numpy as np

cam = cv2.VideoCapture(0)

while True:
    b, img = cam.read()
    if b:
        cv2.imshow("Video", img) #Viser bildet fra cam.read() gjentatte ganger
    else:
        print("The camera is not working")
        break
    key = cv2.waitKey(1)&0xFF
    if key == ord('q'):
        break
cv2.destroyAllWindows()
cam.release()
