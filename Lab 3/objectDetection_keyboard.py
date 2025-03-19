import os
import argparse
import cv2
import numpy as np
import sys
import time
import threading
import importlib.util
from threading import Thread

class Video_PiCamera:
    def __init__(self, resolution=(640, 480), framerate=60):
        # Initializing the PiCamera
        self.stream = cv2.VideoCapture(0)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.stream.set(3, resolution[0])
        self.stream.set(4, resolution[1])
        (self.grabbed, self.frame) = self.stream.read()  # Reading the initial frame
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

# Parsing the arguments
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', required=True)
parser.add_argument('--graph', default='detect.tflite')
parser.add_argument('--labels', default='labelmap.txt')
parser.add_argument('--threshold', default=0.5, type=float)
parser.add_argument('--resolution', default='600x300')
args = parser.parse_args()

model = args.modeldir
graph_n = args.graph
label_ = args.labels
minimum_confidence = args.threshold
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)

# Import TensorFlow Lite interpreter
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter

current_dir = os.getcwd()
tflite_directory = os.path.join(current_dir, model, graph_n)
label_destination = os.path.join(current_dir, model, label_)

# Load label map
with open(label_destination, 'r') as f:
    labels = [line.strip() for line in f.readlines()]
if labels[0] == '???':
    del labels[0]

# Load TFLite model
model_interpreter = Interpreter(model_path=tflite_directory)
model_interpreter.allocate_tensors()
input_details = model_interpreter.get_input_details()
output_details = model_interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
floating_model = (input_details[0]['dtype'] == np.float32)
input_mean = 127.5
input_std = 127.5

# Start video streaming
video_stream = Video_PiCamera(resolution=(imW, imH), framerate=60).start()
time.sleep(1)

def detection():
    while True:
        original_frame = video_stream.read()
        frame = original_frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        model_interpreter.set_tensor(input_details[0]['index'], input_data)
        model_interpreter.invoke()
        
        boxes = model_interpreter.get_tensor(output_details[0]['index'])[0]
        classes = model_interpreter.get_tensor(output_details[1]['index'])[0]
        conf_values = model_interpreter.get_tensor(output_details[2]['index'])[0]

        for i in range(len(conf_values)):
            if minimum_confidence <= conf_values[i] <= 1.0:
                ymin = int(max(1, (boxes[i][0] * imH)))
                xmin = int(max(1, (boxes[i][1] * imW)))
                ymax = int(min(imH, (boxes[i][2] * imH)))
                xmax = int(min(imW, (boxes[i][3] * imW)))
                
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
                
                object_name = labels[int(classes[i])]
                label = f'{object_name}: {int(conf_values[i] * 100)}%'
                label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                label_ymin = max(ymin, label_size[1] + 10)
                
                cv2.rectangle(frame, (xmin, label_ymin - label_size[1] - 10), 
                              (xmin + label_size[0], label_ymin + base_line - 10), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (xmin, label_ymin - 7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.imshow('Object Detection in Stingray', frame)
        
        if cv2.waitKey(1) == ord('q'):
            print("\n Exiting the frame")
            break

    cv2.destroyAllWindows()
    video_stream.stop()

# Create and start the object detection thread
object_detection_thread = threading.Thread(target=detection)
object_detection_thread.start()
