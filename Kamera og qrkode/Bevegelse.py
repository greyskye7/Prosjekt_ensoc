import cv2
import numpy as np

#Video capture
capture = cv2.VideoCapture(0)

#History, Threshold, DetectShadows
fgbg = cv2.createBackgroundSubtractorMOG2(50,200,True)#Tar vekk bakgrunn og viser
#kun det som er foran i video/ i bevegelse
#fgbg = cv2.createBackgroundSubtractorMOG2(300,400,True)

#Keeps track of what frame we're on
frameCount = 0

while(1):
    #Return Value and the current frame
    retUrn, frame = capture.read()

    #Check if a current frame actually exist
    if not retUrn:
        break

    frameCount += 1
    #Resize the frame
    resizedFrame = cv2.resize(frame,(0,0),fx=0.80,fy=0.80)

    #Get the foreground mask
    fgmask = fgbg.apply(resizedFrame)

    #Count all the non zero pixels within the mask
    count = np.count_nonzero(fgmask)

    print('Frame: %d, Pixel Count: %d' % (frameCount, count))

    #Determine how many pixels do you want to detect to be considered "Movement"
    #if (frameCount > 1 and count > 5000):
    if (frameCount > 1 and count > 1000):
        print('Bevegelse')
        cv2.putText(resizedFrame, 'Bevegelse', (10,50),\
        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
    #cv2.imshow('Frame', resizedFrame) #Viser video capture vindu
    #cv2.imshow('Mask', fgmask) # Viser vindu hvor antall pixeler detekteres

    #Make the 2D black and white picture image have three channels:
    #grey_3_channel = cv2.cvtColor(grey,cv2.COLOR_GRAY2BGR)
    numpy_horizontal_concat = np.concatenate((resizedFrame, cv2.cvtColor(fgmask,
cv2.COLOR_GRAY2BGR)), axis = 1)
    cv2.imshow('Video', numpy_horizontal_concat)

    k = cv2.waitKey(1) & 0xff
    if k == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
