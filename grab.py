import cv2
import numpy as np
import serial
from PyQt5 import QtGui, QtWidgets, QtCore  # Add QtCore import
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication

cap = cv2.VideoCapture(1)

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

        self.cap = cv2.VideoCapture(1)
        self.camera_timer = QtCore.QTimer(self)  # Add a QTimer to periodically update the camera feed
        self.camera_timer.timeout.connect(self.update_frame)
        self.camera_timer.start(30)  # Update the frame every 30 milliseconds

        self.redButton.clicked.connect(self.detect_red)
        self.yellowButton.clicked.connect(self.detect_yellow)
        self.greenButton.clicked.connect(self.detect_green)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Display the frame on the QLabel named label_2
            qImg = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label_2.setPixmap(pixmap)  # Use self.label_2 to update the QLabel


    def detect_red(self):
        self.reset_colors()
        self.red = True
        self.ser.write(b'1')
        self.default = b'1'

    def detect_yellow(self):
        self.reset_colors()
        self.yellow = True
        self.ser.write(b'2')
        self.default = b'2'

    def detect_green(self):
        self.reset_colors()
        self.green = True
        self.ser.write(b'3')
        self.default = b'3'

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
