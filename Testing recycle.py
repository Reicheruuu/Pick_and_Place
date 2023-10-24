import cv2
import numpy as np
from PIL import Image
import torch
from torchvision.transforms.functional import resize
import serial

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

# Define a dictionary to map class indices to class names
class_names = {
    0: 'Unknown',
    1: 'Class 0',
    2: 'Biodegradable',
    3: 'Non-Biodegradable'
}

cap = cv2.VideoCapture(2)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Resize the frame
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

    # Convert frame to numpy array
    frame = np.array(frame)

    # Perform inference with bacteria detection model
    results_recycle = recycle(frame)
    print(results_recycle)  # Print model output for debugging

    # Get detected objects and their position for bacteria detection
    boxes_recycle = results_recycle.xyxy[0].cpu().numpy()
    labels_recycle = boxes_recycle[:, -1].astype(int)
    print("Boxes Recycle:", boxes_recycle)

    # Create separate loops for 'biodegradable' and 'non-biodegradable' objects
    for class_name in ['biodegradable', 'non-biodegradable']:
        for i, box in enumerate(boxes_recycle):
            cls = int(box[5])
            conf = box[4]
            confidence_threshold = 0.5
            if (
                cls < len(classes)
                and classes[cls] == class_name
                and conf > confidence_threshold
            ):
                xmin, ymin, xmax, ymax = map(int, box[:4])
                color = (0, 255, 0)  # Green for biodegradable
                if class_name == 'non-biodegradable':
                    color = (0, 0, 255)  # Red for non-biodegradable

                frame = cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

                circle_center_x = (xmin + xmax) // 2
                circle_center_y = (ymin + ymax) // 2
                circle_center = (circle_center_x, circle_center_y)
                circle_radius = 2

                frame = cv2.circle(frame, circle_center, circle_radius, color, -1)

                # Overlay the class name text on the frame
                text = f'Class: {class_name}'
                cv2.putText(frame, text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # Send a byte to Arduino based on the detected class
                if classes[cls] == 'non-biodegradable':
                    byte_to_send = b'1'
                    print('non-biodegradable')
                elif classes[cls] == 'biodegradable':
                    byte_to_send = b'2'
                    print('biodegradable')
                else:
                    byte_to_send = b'0'  # Neutral value if the class is not recognized

                # Send the byte to Arduino
                if byte_to_send != last_sent_byte:
                    ser.write(byte_to_send)
                    last_sent_byte = byte_to_send

    # Display the annotated frame
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imshow('Recycle Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
