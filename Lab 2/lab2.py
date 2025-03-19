import threading
import time
from matplotlib.pylab import *
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.animation as animation
import pigpio
import RPi.GPIO as GPIO
from WheelEncoderGPIO import WheelEncoder
from PlotDataRobot import multiplePlots
import matplotlib.pyplot as plt
from UltrasonicGPIO import HCSR04
import time
import sys
import tty
import termios
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
        
servos = [23,24]
raspi= pigpio.pi()

samples = 5

#creation of two encoders using WheelEncoder class
leftEncoderCount = WheelEncoder(11, 32, 5.65/2)
rightEncoderCount = WheelEncoder(13, 32, 5.65/2)

def Left_forward(n):
    raspi.set_servo_pulsewidth(servos[0], n)

#Value for servo speed forward now an argument that must be passed    
def Right_forward(n):
    raspi.set_servo_pulsewidth(servos[1], n)

def Left_reverse():
    raspi.set_servo_pulsewidth(servos[0], 1250)
    
def Right_reverse():
    raspi.set_servo_pulsewidth(servos[1], 1750)

def Robot_right():
    Left_forward(1750)
    Right_reverse()
    time.sleep(0.3)
    motorStop()

def Robot_left():
    Right_forward(1250)
    Left_reverse()
    time.sleep(0.3)
    motorStop()

def Robot_leftt():
    Right_forward(1250)
    Left_reverse()
    time.sleep(0.6)
    motorStop()

def Robot_rightt():
    Left_forward(1750)
    Right_reverse()
    time.sleep(0.6)
    motorStop()

#robot forward function takes two arguments for each motors servo speed
def Robot_forward(n, m):
    Left_forward(n)
    Right_forward(m)
    time.sleep(.1)

def Robot_reverse():
    Left_reverse()
    Right_reverse()
    time.sleep(.7)
    motorStop()


#Function to stop all motors    
def motorStop():
    for s in servos:
        raspi.set_servo_pulsewidth(s,0)


def straight(leftWheelEncoder, rightWheelEncoder, timer):
    # The role of the controller is to cancel the error of the system
    leftEncoderCount.resetTicks()
    rightEncoderCount.resetTicks()
    
    targetIteration = 10  # Keep this value as 10, it is easier to perform the path
    leftSpeed = 1530  # Try to use a value around 100 higher than the leftSpeed to keep the left wheel stopped
    rightSpeed = 1177  # Try to use a value around 100 lower than the rightSpeed to keep the right wheel stopped
    leftSpeedVar = leftSpeed  # Max speed
    rightSpeedVar = rightSpeed  # Max speed
    
    leftPError = 0
    rightPError = 0
    leftSError = 0
    rightSError = 0
    
    target = 0  # Initialize your target value for number of ticks as 0
    KP = 15  # You can improve this value by testing (always try values between 0 and 50)
    KD = 0  # 5  # You can improve this value by testing
    KI = 3.75  # You can improve this value by testing (a good starting is KP divided by 4)
    
    sampleTime = 0.4  # Keep this value as 0.4 seconds
    timeout = time.time() + timer
    i = 0  # Variable to count the number of iterations
    
    while time.time() < timeout:
        leftError = target - leftWheelEncoder.getTicks()
        rightError = target - rightWheelEncoder.getTicks()

        if (abs(leftError) > 1) or (i == 0):  # Use 1 as a threshold, and it needs to be True when i == 0 (at the initial loop)
            leftSpeed += (leftError * KP) + ((leftError - leftPError) * KD) + (leftSError * KI)
            leftSpeed = max(min(leftSpeedVar, leftSpeed), 1720)
        
        if (abs(rightError) > 1) or (i == 0):  # Use 1 as a threshold, and it needs to be True when i == 0 (at the initial loop)
            rightSpeed -= (rightError * KP) + ((rightError - rightPError) * KD) + (rightSError * KI)
            rightSpeed = min(max(rightSpeedVar, rightSpeed), 1280)

        Robot_forward(leftSpeed, rightSpeed)

        time.sleep(sampleTime)

        leftPError = leftError
        rightPError = rightError
        leftSError += leftError
        rightSError += rightError

        target += targetIteration  # Actualize your target by adding the targetIteration at the end of each iteration
        i += 1  # Actualize the number of iterations

    motorStop()

    # Robot_forward(1420 + 13 * leftError, 1260 - 13 * rightError)  # This is to compensate any errors when the robot stops
    # To compensate the final error, use the speed to keep the wheels stopped, and add or subtract the error
    # multiplied by a number. This number you need to find by testing.

    time.sleep(0.1)
    motorStop()

#Function for encoder output takes wheelEncoder object and a name for the encoder as #arguments
def Encoders(wheelEncoderL, wheelEncoderR, name):
    while(True):
        distL = wheelEncoderL.getCurrentDistance()
        totDistL = wheelEncoderL.getTotalDistance()
        distR= wheelEncoderR.getCurrentDistance()
        totDistR = wheelEncoderR.getCurrentDistance()

        print("\n{} Distance: L {}cm R {}cm".format(name, distL, distR))
        print("\n{} Ticks: L {} R {}".format(name, wheelEncoderL.getTicks(), wheelEncoderR.getTicks()))
        print("\n{} Total Distance: L {} R {}cm".format(name, totDistL, totDistR))
        print("\n{} Total Ticks: L {} R {}".format(name, wheelEncoderL.getTotalTicks(), wheelEncoderR.getTotalTicks()))
        time.sleep(0.01)

# Function for sonar sensor takes HCSR04 object and sample number for accuracy of distance
def Sonar(sensor, samples):
    sensor.move_servo(1400)
    while True:
        s = time.time()
        distance = sensor.measure(samples, "cm")
        e = time.time()
        print("Distance:", distance, "cm")
        print("Used time:", (e - s), "seconds")
        if distance < 10:
            motorStop()
            Robot_reverse()
            time.sleep(0.3)
            avoidance()
            sensor.move_servo(1400)
        time.sleep(0.01)


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def path():
    straight(leftEncoderCount, rightEncoderCount, 1)
    time.sleep(0.1)
    Robot_left()
    time.sleep(0.3)
    straight(leftEncoderCount, rightEncoderCount, 1)
    time.sleep(0.1)
    Robot_right()
    time.sleep(0.4)
    straight(leftEncoderCount, rightEncoderCount, 1)
    time.sleep(0.1)
    Robot_right()
    time.sleep(0.4)
    straight(leftEncoderCount, rightEncoderCount, 1)
    time.sleep(0.1)
    Robot_left()
    time.sleep(0.4)
    straight(leftEncoderCount, rightEncoderCount, 1)
    time.sleep(0.1)


    time.sleep(5)
    path_two()

def path_two():
    straight(leftEncoderCount, rightEncoderCount, 1)
    time.sleep(0.1)
    Robot_right()
    time.sleep(0.3)
    straight(leftEncoderCount, rightEncoderCount, 0.5)
    Robot_leftt()
    time.sleep(0.1)
    straight(leftEncoderCount, rightEncoderCount, 2)
    time.sleep(0.1)
    Robot_rightt()
    time.sleep(0.1)
    straight(leftEncoderCount, rightEncoderCount, 1)
    time.sleep(0.2)
    Robot_left()
    time.sleep(0.6)
    straight(leftEncoderCount, rightEncoderCount, 1)
    time.sleep(0.1)

def move():
    while True:
    # Capture keyboard input
        char = getch()
    
        if char == "w":
            straight(leftEncoderCount, rightEncoderCount, 1)
    
        elif char == 'a':
            Robot_left()

        elif char == 'd':
            Robot_right()

        elif char == 's':
            exit()


samples = 5
sensor = HCSR04(7, 12, 22)

#encoderThread = threading.Thread(target = Encoders, args = (leftEncoderCount,rightEncoderCount,"encoder"))
sonarThread = threading.Thread(target=Sonar, args=(sensor, samples))
moveThread = threading.Thread(target=move, args=())

path_thread = threading.Thread(target=path, args=())
path_thread.start()
sonarThread.start()
moveThread.start()


# Creating and starting the sensor thread

#encoderThread.start()
#moveThread.start()
def avoidance():
    global left_distances, right_distances
    left_distances = sensor.sweep(5, "left")
    right_distances = sensor.sweep(5, "right")

    avg_left = sum(left_distances) / len(left_distances)
    avg_right = sum(right_distances) / len(right_distances)

    if avg_left > avg_right:
        print("Move Left")
        Robot_left()
        time.sleep(0.3)
    elif avg_right > avg_left:
        print("Move Right")
        Robot_right()
        time.sleep(0.3)
    else:
        print("Stop")
    time.sleep(1)





