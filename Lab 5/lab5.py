import threading
import time
import RPi.GPIO as GPIO
from WheelEncoderGPIO import WheelEncoder
from HCSR04 import HCSR04
from object_detection import Video_PiCamera, startObjectDetection
from picamera2 import Picamera2
from tkinter import Tk, Canvas, Label, Button, PhotoImage, StringVar
from PIL import Image, ImageTk
import pigpio
import cv2
import numpy as np
import datetime
from tkinter import filedialog, messagebox
from GUI_path import *
from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import datetime


# Global variables
robot_position = [0, 5]  # Starting position matches GUI (row, col)
robot_heading = 180  # 0: right, 90: down, 180: left, 270: up
obstacle_detected = False
distance_to_obstacle = 0
total_distance_traveled = 0
obstacle_list = []

# Initialize GPIO and Pigpio
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
raspi = pigpio.pi()



# Servo pins
servos = [23, 24]

# Wheel encoders
leftEncoderCount = WheelEncoder(11, 32, 5.65 / 2)
rightEncoderCount = WheelEncoder(13, 32, 5.65 / 2)

# Ultrasonic sensor
sonarSensor = HCSR04(7, 12, 22)


def Left_reverse():
    raspi.set_servo_pulsewidth(servos[0], 1250)
    
def Right_reverse():
    raspi.set_servo_pulsewidth(servos[1], 1750)
    
# Robot Movement Functions
def move_forward(distance):
    straight(leftEncoderCount, rightEncoderCount, distance)  # Use the straight method for PID control
    maze.move_forward()
    

def Robot_left():
    maze.turn_left()
    Right_forward(1250)
    Left_reverse()
    time.sleep(0.3)
    motorStop()
    

def Robot_right():
    maze.turn_right()
    Left_forward(1750)
    Right_reverse()
    time.sleep(0.3)
    motorStop()

def avoidance():
    # Check distances at 45° (left), 90° (center), and 135° (right)
    distances = sonarSensor.check_angles(3)  # 3 samples per angle
    
    left_distance = distances[180]   # Left side distance
    center_distance = distances[70] # Front distance
    right_distance = distances[0] # Right side distance

    # Determine which direction has more space
    if left_distance > right_distance and left_distance > 30:  # 30cm threshold
        print(f"Move Left - Left: {left_distance}cm, Right: {right_distance}cm")
        Robot_left()
        sonarSensor.reset()  # Center the servo
        time.sleep(0.3)
    
    elif right_distance > left_distance and right_distance > 30:  # 30cm threshold
        print(f"Move Right - Left: {left_distance}cm, Right: {right_distance}cm")
        Robot_right()
        sonarSensor.reset()  # Center the servo
        time.sleep(0.3)
    
    elif center_distance < 20:  # If something is too close in front
        print(f"Obstacle too close - Center: {center_distance}cm")
        # Add your stop or reverse logic here
        print("Stop")
    else:
        print(f"Clear path - Center: {center_distance}cm")
        # Add your move forward logic here if needed
    time.sleep(1)
    

def Left_forward(n):
    raspi.set_servo_pulsewidth(servos[0], n)

def Right_forward(n):
    raspi.set_servo_pulsewidth(servos[1], n)
    
def Robot_forward(n, m):
    Left_forward(n)
    Right_forward(m)
    time.sleep(.1)

def motorStop():
    for s in servos:
        raspi.set_servo_pulsewidth(s,0)

def straight(leftWheelEncoder, rightWheelEncoder, timer):
    leftEncoderCount.resetTicks()
    rightEncoderCount.resetTicks()
    
    targetIteration = 10
    leftSpeed = 1530
    rightSpeed = 1177
    leftSpeedVar = leftSpeed
    rightSpeedVar = rightSpeed
    
    leftPError = 0
    rightPError = 0
    leftSError = 0
    rightSError = 0
    
    target = 0
    KP = 15
    KD = 0
    KI = 3.75
    
    sampleTime = 0.4
    timeout = time.time() + timer
    i = 0
    
    while time.time() < timeout:
        leftError = target - leftWheelEncoder.getTicks()
        rightError = target - rightWheelEncoder.getTicks()

        if (abs(leftError) > 1) or (i == 0):
            leftSpeed += (leftError * KP) + ((leftError - leftPError) * KD) + (leftSError * KI)
            leftSpeed = max(min(leftSpeedVar, leftSpeed), 1720)
        
        if (abs(rightError) > 1) or (i == 0):
            rightSpeed -= (rightError * KP) + ((rightError - rightPError) * KD) + (rightSError * KI)
            rightSpeed = min(max(rightSpeedVar, rightSpeed), 1280)

        Robot_forward(leftSpeed, rightSpeed)

        time.sleep(sampleTime)

        leftPError = leftError
        rightPError = rightError
        leftSError += leftError
        rightSError += rightError

        target += targetIteration
        i += 1

    motorStop()
    time.sleep(0.1)
    motorStop()
    
# Maze Traversal
def traverse_maze():
    #global robot_position, robot_heading, obstacle_detected
    # run object_detection 
    # check if you reached the end of the maze if so print done and end execution
    global robot_position, robot_heading, obstacle_detected, distance_to_obstacle, total_distance_traveled
    
    sonarSensor.reset()
    try:
        while True:
            # Check if we've reached the end of the maze (assuming end is at position [GRID_HEIGHT-1, 0])
            if (robot_position[0] == GRID_HEIGHT-2 and robot_position[1] == 0) or maze.end_reached == True:
                print("Maze completed successfully!")
                messagebox.showinfo("Success", "Maze completed successfully!")
                motorStop()
                maze.save_file()
                break
            
            # Measure distance to obstacle
            distance_to_obstacle = sonarSensor.measure(3, "cm")
            display_distance.set(f"{distance_to_obstacle:.2f} cm")
            if distance_to_obstacle < 17 and distance_to_obstacle > 0:  # Obstacle detected
                obstacle_detected = True
                maze.obstacle_detection(distance_to_obstacle)
                motorStop()
                time.sleep(1)
                # Perform avoidance maneuver
                avoidance()
                sonarSensor.reset()
                time.sleep(0.25)
                
                # After avoidance, continue forward
                move_forward(0.50)
                time.sleep(0.18)
                
            else:  # No obstacle detected
                obstacle_detected = False
                move_forward(0.50)
                time.sleep(0.18)
                
                # Update robot position based on heading
                if robot_heading == 0:    # Right
                    robot_position[1] += 1
                elif robot_heading == 90:  # Down
                    robot_position[0] += 1
                elif robot_heading == 180:  # Left
                    robot_position[1] -= 1
                elif robot_heading == 270:  # Up
                    robot_position[0] -= 1
                
                # Keep position within grid bounds
                robot_position[0] = max(0, min(GRID_HEIGHT-1, robot_position[0]))
                robot_position[1] = max(0, min(GRID_WIDTH-1, robot_position[1]))
                
                total_distance_traveled += 1
                    
                # Small delay to prevent overwhelming the system
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("Maze traversal interrupted by user")
    finally:
        motorStop()
        GPIO.cleanup()
        raspi.stop()
    
# Main Program
if __name__ == "__main__":
    root=tk.Tk()
    root.geometry("500x800")
    root.title("Robot Path")
    root.config(background="black")

    title = Label(root, 
                text="Robot Path", font=('Arial', 10, 'bold'), fg='white', bg='black',
                relief = RAISED, bd=5,
                padx=5, pady=5)
    title.pack()
    display_distance = tk.StringVar()
    display_distance.set(str(float(0)))
    maze = GUI(root, display_distance)
    label = Label(root, textvariable=display_distance, font=('Arial', 10), bg='#000000', fg='#FFFFFF')
    label.pack()
    save_button = Button(root, text='save', command=maze.save_file, font=('Arial', 10), bg='green', fg='white')
    save_button.pack(pady=10)
    
    
    startObjectDetection()
    traverse_maze()
    root.mainloop()
   