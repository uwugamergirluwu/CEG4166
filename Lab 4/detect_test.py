import numpy as np
import cv2
import threading
import time
from picamera2 import Picamera2

# Initialize Picamera2
picam2 = Picamera2()
# Configure the height and width of the frame
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Allow camera to warm up
time.sleep(2)

# Load the face detection model
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_detector = cv2.CascadeClassifier(cascade_path)

def face_detection_test(anything1, anything2):
    while True:
        # Capture frame as NumPy array
        img = picam2.capture_array()
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_detector.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=5, minSize=(20, 20)
        )
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Display the image
        cv2.imshow('Face Detection', img)
        
        # Press 'ESC' key to exit
        k = cv2.waitKey(30) & 0xFF
        if k == 27:
            break
    
    cv2.destroyAllWindows()
    picam2.stop()

# Start face detection in a separate thread
detection_thread = threading.Thread(target=face_detection_test, args=('any1', 'any2'))
detection_thread.start()
