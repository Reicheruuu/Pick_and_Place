import cv2
import numpy as np
import time
import serial

# Open serial connection to Arduino
arduino_port = 'COM7'  # Replace with the appropriate port for your Arduino
ser = serial.Serial(arduino_port, baudrate=115200)

cap = cv2.VideoCapture(2)

# Set the frame rate to 60 fps
cap.set(cv2.CAP_PROP_FPS, 60)

# Variables to keep track of sent bytes and task execution
last_sent_byte = b'0'  # Initialize with a neutral value

contours = 100

while True:
    cr = 0
    cb = 0
    cg = 0
    ret, im = cap.read()
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    # Color detection masks
    lowred = np.array([0, 100, 100], dtype=np.uint8)
    highred = np.array([10, 255, 255], dtype=np.uint8)
    maskr = cv2.inRange(hsv, lowred, highred)

    lowgreen = np.array([44, 54, 63], dtype=np.uint8)
    highgreen = np.array([90, 255, 255], dtype=np.uint8)
    maskg = cv2.inRange(hsv, lowgreen, highgreen)

    lowyellow = np.array([20, 50, 100], dtype=np.uint8)
    highyellow = np.array([42, 255, 255], dtype=np.uint8)
    masky = cv2.inRange(hsv, lowyellow, highyellow)

    cr = cv2.countNonZero(maskr)
    cg = cv2.countNonZero(maskg)
    cy = cv2.countNonZero(masky)

    if cr > 4000 and last_sent_byte != b'1':
            print('red')
            ser.write(b'1')  # Send a byte to Arduino
            last_sent_byte = b'1'
    elif cg > 4000 and last_sent_byte != b'2':
            print('green')
            ser.write(b'2')  # Send a different byte to Arduino
            last_sent_byte = b'2'
    elif cy > 4000 and last_sent_byte != b'3':
            print('yellow')
            ser.write(b'3')  # Send another byte to Arduino
            last_sent_byte = b'3'
    elif cr <= 4000 and cg <= 4000 and cy <= 4000 and last_sent_byte != b'0':
            print('No clear color match, staying at 0 degrees')
            ser.write(b'0')  # Send 0 byte to Arduino to stay at 0 degrees
            last_sent_byte = b'0'

    if cr > 4000:
        contours, _ = cv2.findContours(maskr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Draw red bounding box

    elif cg > 4000:
        contours, _ = cv2.findContours(maskg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw green bounding box

    elif cy > 4000:
        contours, _ = cv2.findContours(masky, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 255), 2)  # Draw yellow bounding box

    cv2.imshow("camera", im)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break


# Close the serial connection
ser.close()
cap.release()
cv2.destroyAllWindows()