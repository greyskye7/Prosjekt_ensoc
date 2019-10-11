import cv2
import urllib
import numpy as np

req = urllib.urlopen('https://hundehelse.no/wp-content/uploads\
/2016/02/Silly-Dachshund-000017989917_Large-e1455617905890.jpg')

arr = np.asarray(bytearray(req.read()), dtype = np.uint8)
img = cv2.imdecode(arr, -1) #Load as it is #Setter om det er farge/sort hvitt
img = cv2.resize(img, (320,320))

cv2.imshow('Doggy', img) #Overskrift for bildet
if cv2.waitKey() & 0xff == 27: quit()
cv2.destroyAllWindows()
