import cv2
import numpy as np
import serial
from PyQt5 import QtGui, QtWidgets, QtCore  # Add QtCore import
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication

cap = cv2.VideoCapture(1)
countour_area = 0

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("Color.ui", self)

        self.setWindowTitle("Color Detection")

        self.tabWidget.setCurrentIndex(0)
        self.arduino_port = 'COM7'  # Replace with the appropriate port for your Arduino
        self.ser = serial.Serial(self.arduino_port, baudrate=9600)

        self.red = False
        self.yellow = False
        self.green = False
        self.default = b'0'
        self.countour_area = 100
        self.cap = cv2.VideoCapture(2)
        self.redButton.clicked.connect(self.detect_red)
        self.yellowButton.clicked.connect(self.detect_yellow)
        self.greenButton.clicked.connect(self.detect_green)
        # Start the camera feed update loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_camera_feed)
        self.timer.start(33)  # 30 FPS (1000 ms / 30 frames)

    def update_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            self.update_frame(frame)

    def update_frame(self, frame):
        # Convert the frame to RGB format for proper display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create a QImage from the frame data
        height, width, channel = frame_rgb.shape
        qImg = QtGui.QImage(frame_rgb.data, width, height, QtGui.QImage.Format_RGB888)

        # Create a QPixmap from the QImage
        pixmap = QtGui.QPixmap.fromImage(qImg)

        # Set the QPixmap to the label_2 QLabel
        self.label_2.setPixmap(pixmap)

    def detect_red(self):
        self.reset_colors()

        ret, frame = self.cap.read()
        if ret:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define color range for red detection
            r_lower1 = np.array([0, 50, 50])
            r_upper1 = np.array([10, 255, 255])
            r_lower2 = np.array([170, 50, 50])
            r_upper2 = np.array([180, 255, 255])

            # Create a mask for red color
            r_mask = cv2.inRange(hsv_frame, r_lower1, r_upper1) + cv2.inRange(hsv_frame, r_lower2, r_upper2)

            # Find contours for red color
            contours_r, _ = cv2.findContours(r_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Check if red color is detected and its contour area is sufficient
            if len(contours_r) > 0 and cv2.contourArea(contours_r[0]) > countour_area:
                self.red = True
                self.ser.write(b'1')
                self.default = b'1'
                print('Red detected and command sent to Arduino')
            else:
                print('Red not detected')

        # Update the GUI elements accordingly
        self.update_frame(frame)

    def detect_yellow(self):
        self.reset_colors()

        ret, frame = self.cap.read()
        if ret:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define color range for yellow detection
            y_lower1 = np.array([20, 100, 100])
            y_upper1 = np.array([30, 255, 255])

            # Create a mask for yellow color
            y_mask = cv2.inRange(hsv_frame, y_lower1, y_upper1)

            # Find contours for yellow color
            contours_y, _ = cv2.findContours(y_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Check if yellow color is detected and its contour area is sufficient
            if len(contours_y) > 0 and cv2.contourArea(contours_y[0]) > countour_area:
                self.yellow = True
                self.ser.write(b'2')
                self.default = b'2'
                print('Yellow detected and command sent to Arduino')
            else:
                print('Yellow not detected')

        # Update the GUI elements accordingly
        self.update_frame(frame)

    def detect_green(self):
        self.reset_colors()

        ret, frame = self.cap.read()
        if ret:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define color range for green detection
            g_lower1 = np.array([40, 40, 40])
            g_upper1 = np.array([86, 255, 255])

            # Create a mask for green color
            g_mask = cv2.inRange(hsv_frame, g_lower1, g_upper1)

            # Find contours for green color
            contours_g, _ = cv2.findContours(g_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Check if green color is detected and its contour area is sufficient
            if len(contours_g) > 0 and cv2.contourArea(contours_g[0]) > countour_area:
                self.green = True
                self.ser.write(b'3')
                self.default = b'3'
                print('Green detected and command sent to Arduino')
            else:
                print('Green not detected')

        # Update the GUI elements accordingly
        self.update_frame(frame)

    def reset_colors(self):
        self.red = False
        self.yellow = False
        self.green = False
        self.ser.write(b'0')
        self.default = b'0'



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
