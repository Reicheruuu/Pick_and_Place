import tkinter as tk
from tkinter import Canvas, Label, Button
from PIL import Image, ImageTk
import cv2
import numpy as np
import torch
from torchvision.transforms.functional import resize
import serial
import threading

# Open serial connection to Arduino
arduino_port = 'COM7'  # Replace with the appropriate port for your Arduino
ser = serial.Serial(arduino_port, baudrate=115200)
last_sent_byte = b'0'  # Initialize with a neutral value

# Load the bacteria detection model
recycle = torch.hub.load('ultralytics/yolov5', 'custom', path='PICK AND PLACE WITH COLOR DETECTION/recycle2/weights/best.pt')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
recycle = recycle.to(device)
recycle.eval()

# Define the list of classes for detection
classes = ['-', '0', 'biodegradable', 'non-biodegradable']

cap = cv2.VideoCapture(0)

# Create the root window
window = tk.Tk()
window.title('Pick and Place')
window.maxsize(900, 600)
window.resizable(0, 0)

# Create Frame1 with logo and title
frame1 = tk.Frame(window, width=900, height=100, bg='#3A6B35')
frame1.pack()
img1 = Image.open("logo.png")
resized_image = img1.resize((80, 80))
img_logo = ImageTk.PhotoImage(resized_image)
canvas1 = Canvas(frame1, width=80, height=80, bg='#3A6B35', highlightthickness=0)
canvas1.create_image(40, 40, image=img_logo)
canvas1.place(x=20, y=10)
label_title = Label(frame1, text='PICK N\' PLACE \n LET\'S SEGREGATE!', font=('Georgia', 28, 'bold'), fg='white', bg='#3A6B35')
label_title.place(x=100, y=20)

# Create Frame2
frame2 = tk.Frame(window, width=900, height=500, bg='#CBD18F')
frame2.pack()

# Camera
canvas2 = Canvas(frame2, width=450, height=370)
canvas2.place(x=55, y=60)

# Variable to indicate whether object detection is active
object_detection_active = False

# Create a function to continuously update the Canvas with the camera feed
def update_camera_feed():
    ret, frame = cap.read()
    if ret:
        # Convert the frame to RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize the frame if needed
        max_size = 900
        height, width, _ = frame.shape
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        frame = resize(Image.fromarray(frame), (new_width, new_height))

        # Create a PhotoImage from the frame
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))

        # Update the Canvas with the new frame
        canvas2.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas2.photo = photo  # Keep a reference to prevent garbage collection

    # Schedule the function to run again after a delay (e.g., 10 ms)
    if object_detection_active:
        window.after(10, update_camera_feed)

# Function to perform object detection for "Biodegradable" items
def detect_biodegradable():
    global last_sent_byte
    global object_detection_active
    while object_detection_active:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = frame.shape
        max_size = 900
        if width > height:
            new_width = max_size
            new_height = int(height / (width / max_size))
        else:
            new_height = max_size
            new_width = int(width / (height / max_size))
        frame = resize(Image.fromarray(frame), (new_height, new_width))

        frame = np.array(frame)

        results_recycle = recycle(frame)
        print(results_recycle)

        boxes_recycle = results_recycle.xyxy[0].cpu().numpy()
        labels_recycle = boxes_recycle[:, -1].astype(int)
        print("Boxes Recycle:", boxes_recycle)

        # Process "Biodegradable" objects only
        for i, box in enumerate(boxes_recycle):
            cls = int(box[5])
            conf = box[4]
            confidence_threshold = 0.5
            if (
                    cls < len(classes)
                    and classes[cls] == 'biodegradable'
                    and conf > confidence_threshold
            ):
                xmin, ymin, xmax, ymax = map(int, box[:4])
                color = (0, 255, 0)  # Green for biodegradable

                frame = cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

                circle_center_x = (xmin + xmax) // 2
                circle_center_y = (ymin + ymax) // 2
                circle_center = (circle_center_x, circle_center_y)
                circle_radius = 2

                frame = cv2.circle(frame, circle_center, circle_radius, color, -1)

                text = 'Class: Biodegradable'
                cv2.putText(frame, text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # Send a byte to Arduino for "Biodegradable"
                byte_to_send = b'2'
                if byte_to_send != last_sent_byte:
                    ser.write(byte_to_send)
                    last_sent_byte = byte_to_send

        # Update the GUI with the modified frame (if needed)
        if object_detection_active:
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            canvas2.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas2.photo = photo
        # Schedule the next object detection after a delay (e.g., 100 ms)
        if object_detection_active:
            window.after(100, detect_biodegradable)

# Function to perform object detection for "Non-Biodegradable" items
def detect_non_biodegradable():
    global last_sent_byte
    while object_detection_active:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = frame.shape
        max_size = 900
        if width > height:
            new_width = max_size
            new_height = int(height / (width / max_size))
        else:
            new_height = max_size
            new_width = int(width / (height / max_size))
        frame = resize(Image.fromarray(frame), (new_height, new_width))

        frame = np.array(frame)

        results_recycle = recycle(frame)
        print(results_recycle)

        boxes_recycle = results_recycle.xyxy[0].cpu().numpy()
        labels_recycle = boxes_recycle[:, -1].astype(int)
        print("Boxes Recycle:", boxes_recycle)

        # Process "Non-Biodegradable" objects only
        for i, box in enumerate(boxes_recycle):
            cls = int(box[5])
            conf = box[4]
            confidence_threshold = 0.5
            if (
                    cls < len(classes)
                    and classes[cls] == 'non-biodegradable'
                    and conf > confidence_threshold
            ):
                xmin, ymin, xmax, ymax = map(int, box[:4])
                color = (0, 0, 255)  # Red for non-biodegradable

                frame = cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

                circle_center_x = (xmin + xmax) // 2
                circle_center_y = (ymin + ymax) // 2
                circle_center = (circle_center_x, circle_center_y)
                circle_radius = 2

                frame = cv2.circle(frame, circle_center, circle_radius, color, -1)

                text = 'Class: Non-Biodegradable'
                cv2.putText(frame, text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # Send a byte to Arduino for "Non-Biodegradable"
                byte_to_send = b'1'
                if byte_to_send != last_sent_byte:
                    ser.write(byte_to_send)
                    last_sent_byte = byte_to_send

        # Update the GUI with the modified frame (if needed)
        if object_detection_active:
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            canvas2.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas2.photo = photo


# Function to start object detection
def start_object_detection():
    global object_detection_active
    object_detection_active = True
    threading.Thread(target=detect_biodegradable).start()  # Start the object detection in a new thread

# Function to stop object detection
def stop_object_detection():
    global object_detection_active
    object_detection_active = False

# Create buttons to start and stop object detection
start_button = Button(frame2, text='Start Object Detection', font=('Georgia', 20), fg='#3A6B35', borderwidth=2,
                 relief='ridge', bg='#CBD18F', width=20, height=2, cursor='hand2', command=start_object_detection)
stop_button = Button(frame2, text='Stop Object Detection', font=('Georgia', 20), fg='#3A6B35', borderwidth=2,
                 relief='ridge', bg='#CBD18F', width=20, height=2, cursor='hand2', command=stop_object_detection)

# Create buttons
button1 = Button(frame2, text='BIODEGRADABLE', font=('Georgia', 20), fg='#3A6B35', borderwidth=2,
                 relief='ridge', bg='#CBD18F', width=20, height=2, cursor='hand2', command=start_object_detection)
button2 = Button(frame2, text='NON-BIODEGRADABLE', font=('Georgia', 20), fg='#3A6B35', borderwidth=2,
                 relief='ridge', bg='#CBD18F', width=20, height=2, cursor='hand2', command=start_object_detection)

button1.place(x=555, y=150)
button2.place(x=555, y=250)

# Start updating the camera feed
update_camera_feed()

# Run the main GUI loop
window.mainloop()
