import cv2
import tkinter as tk
import numpy as np
import time
from PIL import Image, ImageDraw, ImageTk
import gc
import serial
from tkinter import ttk
from grab import * # Function for grabbing the Object
from pyfirmata import Arduino, SERVO

# Color contour disable (boolean)
red = False
yellow = False
blue = False
orange = False
green = False
violet = False

#RED
r_lower1 = np.array([0, 50, 50])
r_upper1 = np.array([10, 255, 255])
r_lower2 = np.array([170,50,50])
r_upper2 = np.array([180,255,255])

#YELLOW
y_lower1 = np.array([20, 100, 100])
y_upper1 = np.array([30, 255, 255])
y_lower2 = np.array([0, 0, 0])
y_upper2 = np.array([0, 0, 0])

#BLUE
b_lower1 = np.array([100,150,0])
b_upper1 = np.array([140,255,255])
b_lower2 = np.array([0, 0, 0])
b_upper2 = np.array([0, 0, 0])

#ORANGE
o_lower1 = np.array([11, 100, 20])
o_upper1 = np.array([20, 255, 255])
o_lower2 = np.array([0, 0, 0])
o_upper2 = np.array([0, 0, 0])

#GREEN
g_lower1 = np.array([40, 40, 40])
g_upper1 = np.array([86, 255, 255])
g_lower2 = np.array([0, 0, 0])
g_upper2 = np.array([0, 0, 0])

#VIOLET
v_lower1 = np.array([129, 50, 70])
v_upper1 = np.array([158, 255, 255])
v_lower2 = np.array([0, 0, 0])
v_upper2 = np.array([0, 0, 0])

# Serial Setup
port = "COM4"
ser = serial.Serial(port, baudrate=9600, timeout=0.2)

# Camera Movement
x_initial = 390 # Middle of Arm
x_offset = 0

# Default Servo values
def_1 = "70";
def_2 = "170";
def_3 = "120";

mid = 0

# GUI AND CAMERA/CV SETUP
cap = cv2.VideoCapture(0)

root = tk.Tk()

# Icon
icon = "images/bg.png"
photo = tk.PhotoImage(file = icon)

n_img = Image.open(icon)
e_img = n_img.resize((1000, 600))
e_img = ImageTk.PhotoImage(e_img)

root.iconphoto(False, photo)

WIDTH = 1000 # WIDTH OF GUI
HEIGHT = 600 # HEIGHT OF GUI

v_WIDTH = int(cap.get(3))
v_HEIGHT = int(cap.get(4))

# Button Width
B_W = 10

# Grip Value
grip = "105"

# Variable of buttons
is_open = 1

Grab = "0"
distance = 0
area = 0

counter = 0

#####################
# CREATED FUNCTIONS #
#####################
def sendData(d):
    ser.write(bytes(d, "utf8"))
    print("Sending datas: " + d)

# Function for getting the object
def getOffset():
    global def_1, mid, x, h, x_initial # 304

    if mid != None:
        if not ((float(mid) > x_initial - 20) and (float(mid) < x_initial + 20)):
            off = x_initial - float(mid)

            off = round(off / 10)
            def_1 = round(float(def_1) + off)
            def_1 = str(def_1)

            if int(def_1) < 40:
                def_1 = "40"

def alwaysSend():
    global grip, def_1, def_2, def_3, Grab
    global red, yellow, blue, orange, green, violet, distance, area, grab, mid, x_initial,counter

    if red or yellow or blue or orange or green or violet:
        getOffset()

    # sendData
    servo1 = def_1
    servo2 = def_2
    servo3 = def_3
    grip = grip

    #print(inRange(int(round(float(mid))), x_initial-20, x_initial+20))
    """
        if inRange(int(round(float(mid))), x_initial-20, x_initial+20):
        TypeError: float() argument must be a string or a number, not 'NoneType'"""
    # if inRange(int(round(float(mid))), x_initial-20, x_initial+20):

    if mid is not None and inRange(int(round(float(mid))), x_initial - 20, x_initial + 20):
        servo2, servo3 = grab(distance, area)

    grip = "105"

    if servo2 != def_2:
        Grab = "1"
        grip = "180"

    if int(servo1) > 120:
        servo1 = "90"

    if int(servo1) < 60:
        servo1 = "60"

    data = servo1 + "-" + servo2 + "-" + servo3 + "-" + grip + "-" + Grab

    if counter == 0:
        sendData(data)

    if Grab == "1":
        grip = "105"
        counter += 1

    if counter == 6:
        counter = 0
        Grab = "0"

    root.after(2100, alwaysSend)

def chosen_color(color):
    global red, yellow, blue, orange, green, violet
    if color == "red":
        red = True
        yellow = False
        blue = False
        orange = False
        green = False
        violet = False
        return 0

    if color == 'yellow':
        yellow = True
        red = False
        blue = False
        orange = False
        green = False
        violet = False
        return 0

    if color == 'blue':
        blue = True
        red = False
        yellow = False
        orange = False
        green = False
        violet = False
        return 0

    if color == 'orange':
        orange = True
        red = False
        yellow = False
        blue = False
        green = False
        violet = False
        return 0

    if color == 'green':
        green = True
        red = False
        yellow = False
        blue = False
        orange = False
        violet = False
        return 0

    if color == 'violet':
        violet = True
        red = False
        yellow = False
        blue = False
        orange = False
        green = False
        return 0

def convert_to_image(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame)
    return image

def update_frame():
    START_TIME = time.time()
    global image, x, w, mid, distance, area, counter
    _, frame = cap.read()
    # frame = cv2.rotate(frame, cv2.ROTATE_180) # Remove if camera is stable

    alpha = 1
    beta = 0
    frame = cv2.addWeighted(frame, alpha, np.zeros(frame.shape, frame.dtype), 0, beta)

    if frame is not None:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        r_lower_mask = cv2.inRange(image, r_lower1, r_upper1)
        r_upper_mask = cv2.inRange(image, r_lower2, r_upper2)
        r_full_mask = r_lower_mask + r_upper_mask;

        y_lower_mask = cv2.inRange(image, y_lower1, y_upper1)
        y_upper_mask = cv2.inRange(image, y_lower2, y_upper2)
        y_full_mask = y_lower_mask + y_upper_mask;

        b_lower_mask = cv2.inRange(image, b_lower1, b_upper1)
        b_upper_mask = cv2.inRange(image, b_lower2, b_upper2)
        b_full_mask = b_lower_mask + b_upper_mask;

        o_lower_mask = cv2.inRange(image, o_lower1, o_upper1)
        o_upper_mask = cv2.inRange(image, o_lower2, o_upper2)
        o_full_mask = o_lower_mask + o_upper_mask;

        g_lower_mask = cv2.inRange(image, g_lower1, g_upper1)
        g_upper_mask = cv2.inRange(image, g_lower2, g_upper2)
        g_full_mask = g_lower_mask + g_upper_mask;

        v_lower_mask = cv2.inRange(image, v_lower1, v_upper1)
        v_upper_mask = cv2.inRange(image, v_lower2, v_upper2)
        v_full_mask = v_lower_mask + v_upper_mask;

        contours_r, hierarchy = cv2.findContours(r_full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_y, hierarchy_y = cv2.findContours(y_full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_b, hierarchy_b = cv2.findContours(b_full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_o, hierarchy_o = cv2.findContours(o_full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_g, hierarchy_g = cv2.findContours(g_full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_v, hierarchy_v = cv2.findContours(v_full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if red:
            if len(contours_r) !=0:
                for contour in contours_r:
                    if cv2.contourArea(contour) > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.putText(frame, "Red", (x, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 2)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
                        break

                area = cv2.contourArea(contour)
                s = "Area of Object: " + str(area)
                distance = 2*(10**(-7))* (area**2) - 0.0044 * (area) + 45.19
                d = "Distance of Object: " + str(round(distance, 2))

                try:
                    mid = str(x + (w / 2))
                except:
                    mid = None

                cv2.putText(frame, s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                cv2.putText(frame, d, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                # cv2.putText(frame, mid, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        if yellow:
            if len(contours_y) != 0:
                for contour in contours_y:
                    if cv2.contourArea(contour) > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.putText(frame, "Yellow", (x, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,255), 2)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,255), 3)
                        break

                area = cv2.contourArea(contour)
                distance = 2*(10**(-7))* (area**2) - 0.0044 * (area) + 45.19
                d = "Distance of Object: " + str(round(distance, 2))
                s = "Area of Object: " + str(area)

                try:
                    mid = str(x + (w / 2))
                except:
                    mid = None

                cv2.putText(frame, s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                cv2.putText(frame, d, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                # cv2.putText(frame, mid, (10, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)

        if blue:
            if len(contours_b) != 0:
                for contour in contours_b:
                    if cv2.contourArea(contour) > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.putText(frame, "Blue", (x, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 2)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)
                        break

                area = cv2.contourArea(contour)
                distance = 2*(10**(-7))* (area**2) - 0.0044 * (area) + 45.19
                d = "Distance of Object: " + str(round(distance, 2))
                s = "Area of Object: " + str(area)

                try:
                    mid = str(x + (w / 2))
                except:
                    mid = None

                cv2.putText(frame, s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                cv2.putText(frame, d, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                # cv2.putText(frame, mid, (10, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)

        if orange:
            if len(contours_o) != 0:
                for contour in contours_o:
                    if cv2.contourArea(contour) > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.putText(frame, "Orange", (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 165, 255), 2)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 165, 255), 3)
                        break

                area = cv2.contourArea(contour)
                s = "Area of Object: " + str(area)
                distance = 2 * (10 ** (-7)) * (area ** 2) - 0.0044 * (area) + 45.19
                d = "Distance of Object: " + str(round(distance, 2))

                try:
                    mid = str(x + (w / 2))
                except:
                    mid = None

                cv2.putText(frame, s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, d, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # cv2.putText(frame, mid, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        if green:
            if len(contours_g) != 0:
                for contour in contours_g:
                    if cv2.contourArea(contour) > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.putText(frame, "Green", (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                        break

                area = cv2.contourArea(contour)
                s = "Area of Object: " + str(area)
                distance = 2 * (10 ** (-7)) * (area ** 2) - 0.0044 * (area) + 45.19
                d = "Distance of Object: " + str(round(distance, 2))

                try:
                    mid = str(x + (w / 2))
                except:
                    mid = None

                cv2.putText(frame, s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, d, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # cv2.putText(frame, mid, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        if violet:
            if len(contours_v) != 0:
                for contour in contours_v:
                    if cv2.contourArea(contour) > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.putText(frame, "Violet", (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (148, 0, 211), 2)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (148, 0, 211), 3)
                        break

                area = cv2.contourArea(contour)
                s = "Area of Object: " + str(area)
                distance = 2 * (10 ** (-7)) * (area ** 2) - 0.0044 * (area) + 45.19
                d = "Distance of Object: " + str(round(distance, 2))

                try:
                    mid = str(x + (w / 2))
                except:
                    mid = None

                cv2.putText(frame, s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, d, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # cv2.putText(frame, mid, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        image = convert_to_image(frame)

    photo.paste(image)
    root.after(round(10), update_frame)

root.title("EROVOUTIKA COLOR PICKER")
root.minsize(WIDTH, HEIGHT)
root.resizable(0,0)

root['bg'] = '#131113'

# Erovoutika Image
image_l = tk.Label(root, image = e_img)
image_l.config(bg='#131113')
image_l.place(relx=0.5, rely=0.5, anchor='center')

# GUI ELEMENT
canvas = tk.Canvas(root, width=463, height=466, bg='red')
canvas.place(relx=0.295, rely=0.557, anchor='center')

# BUTTONS
# If clicked a color disable the contours for other color
B_W = 10
BUTTON_HEIGHT = 0.15

rstyle = ttk.Style()
rstyle.configure('VerticalRoundedRedButton.TButton', borderwidth=0, relief='flat', background='red', foreground='red',
                padding=5, bordercolor='white', focusthickness=0, font=('Helvetica', 12, 'bold'))

rstyle.map('VerticalRoundedRedButton.TButton', background=[('active', 'red'), ('pressed', '!disabled', 'dark red')])

rstyle.layout('VerticalRoundedRedButton.TButton', [('Button.focus', {'children': [('Button.border', {'children': [('Button.padding', {'children': [('Button.label', {'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})])

r_button = ttk.Button(root, text="RED", width=B_W, command=lambda: chosen_color('red'), style='VerticalRoundedRedButton.TButton')
r_button.place(relx=0.65, rely=0.25, relheight=BUTTON_HEIGHT)

ystyle = ttk.Style()
ystyle.configure('VerticalRoundedYellowButton.TButton', borderwidth=0, relief='flat', background='yellow', foreground='#F6BE00',
                padding=5, bordercolor='white', focusthickness=0, font=('Helvetica', 12, 'bold'))

ystyle.map('VerticalRoundedYellowButton.TButton', background=[('active', 'yellow'), ('pressed', '!disabled', 'dark yellow')])

ystyle.layout('VerticalRoundedYellowButton.TButton', [('Button.focus', {'children': [('Button.border', {'children': [('Button.padding', {'children': [('Button.label', {'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})])

y_button = ttk.Button(root, text="YELLOW", width=B_W, command=lambda: chosen_color('yellow'), style='VerticalRoundedYellowButton.TButton')
y_button.place(relx=0.65, rely=0.45, relheight=BUTTON_HEIGHT)

bstyle = ttk.Style()
bstyle.configure('VerticalRoundedBlueButton.TButton', borderwidth=0, relief='flat', background='blue', foreground='blue',
                padding=5, bordercolor='white', focusthickness=0, font=('Helvetica', 12, 'bold'))

bstyle.map('VerticalRoundedBlueButton.TButton', background=[('active', 'blue'), ('pressed', '!disabled', 'dark blue')])

bstyle.layout('VerticalRoundedBlueButton.TButton', [('Button.focus', {'children': [('Button.border', {'children': [('Button.padding', {'children': [('Button.label', {'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})])

b_button = ttk.Button(root, text="BLUE", width=B_W, command=lambda: chosen_color('blue'), style='VerticalRoundedBlueButton.TButton')
b_button.place(relx=0.65, rely=0.65, relheight=BUTTON_HEIGHT)

ostyle = ttk.Style()
ostyle.configure('VerticalRoundedOrangeButton.TButton', borderwidth=0, relief='flat', background='orange', foreground='orange',
                padding=5, bordercolor='white', focusthickness=0, font=('Helvetica', 12, 'bold'))

ostyle.map('VerticalRoundedOrangeButton.TButton', background=[('active', 'orange'), ('pressed', '!disabled', 'dark orange')])

ostyle.layout('VerticalRoundedOrangeButton.TButton', [('Button.focus', {'children': [('Button.border', {'children': [('Button.padding', {'children': [('Button.label', {'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})])

o_button = ttk.Button(root, text="ORANGE", width=B_W, command=lambda: chosen_color('orange'), style='VerticalRoundedOrangeButton.TButton')
o_button.place(relx=0.80, rely=0.25, relheight=BUTTON_HEIGHT)

gstyle = ttk.Style()
gstyle.configure('VerticalRoundedGreenButton.TButton', borderwidth=0, relief='flat', background='green', foreground='green',
                padding=5, bordercolor='white', focusthickness=0, font=('Helvetica', 12, 'bold'))

gstyle.map('VerticalRoundedGreenButton.TButton', background=[('active', 'green'), ('pressed', '!disabled', 'dark green')])

gstyle.layout('VerticalRoundedGreenButton.TButton', [('Button.focus', {'children': [('Button.border', {'children': [('Button.padding', {'children': [('Button.label', {'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})])

g_button = ttk.Button(root, text="GREEN", width=B_W, command=lambda: chosen_color('green'), style='VerticalRoundedGreenButton.TButton')
g_button.place(relx=0.80, rely=0.45, relheight=BUTTON_HEIGHT)

vstyle = ttk.Style()
vstyle.configure('VerticalRoundedVioletButton.TButton', borderwidth=0, relief='flat', background='violet', foreground='violet',
                padding=5, bordercolor='white', focusthickness=0, font=('Helvetica', 12, 'bold'))

vstyle.map('VerticalRoundedVioletButton.TButton', background=[('active', 'violet'), ('pressed', '!disabled', 'dark violet')])

vstyle.layout('VerticalRoundedVioletButton.TButton', [('Button.focus', {'children': [('Button.border', {'children': [('Button.padding', {'children': [('Button.label', {'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})], 'sticky': 'nsew'})])

v_button = ttk.Button(root, text="VIOLET", width=B_W, command=lambda: chosen_color('violet'), style='VerticalRoundedVioletButton.TButton')
v_button.place(relx=0.80, rely=0.65, relheight=BUTTON_HEIGHT)

# ---------------- Main Execution ---------------

_, frame = cap.read()
if frame is not None:
    image = convert_to_image(frame)
    photo = ImageTk.PhotoImage(image=image)
    canvas.create_image(v_WIDTH, v_HEIGHT, image=photo, anchor='se')

# Start the Video
if __name__ == '__main__':
	update_frame()
	alwaysSend()

# Creating GUI
root.mainloop()

cap.release()
gc.collect()