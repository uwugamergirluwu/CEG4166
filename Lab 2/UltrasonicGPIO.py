import RPi.GPIO as gpio
import time
import threading

left_distances=[]
right_distances=[]
class HCSR04:
    # Encapsulates the attributes and methods to use the HC-SR04 ultrasonic distance sensor
    servo = 0
    trig = 0
    echo = 0
    const_cm = 17014.50
    const_in = 6698.62
    const_ft = 558.2
    pwm = 0

    def __init__(self, trig, echo, servo):
        self.trig = trig
        self.echo = echo
        self.servo = servo

        gpio.setmode(gpio.BOARD)

        gpio.setup(self.trig, gpio.OUT)
        gpio.setup(self.echo, gpio.IN)
        gpio.setup(self.servo, gpio.OUT)

        gpio.output(self.trig, False)

        # ✅ Correct PWM initialization
        self.pwm = gpio.PWM(self.servo, 50)  # Use self.servo instead of hardcoded 22
        self.pwm.start(0)  # Start PWM with 0% duty cycle
        time.sleep(0.3)  # Allow components to settle



    def __del__(self):
        gpio.cleanup()
        print("All cleaned up.")

    # Measures the distance and returns the distance in the desired unit
    def measure(self, samples, unit):
        count = 0
        distance = 0.0
        pulse_start = 0
        pulse_end = 0
        acc = 0

        while count < samples:
            gpio.output(self.trig, True)
            time.sleep(0.00001)
            gpio.output(self.trig, False)

            # Wait for the echo pin to go HIGH
            while gpio.input(self.echo) == 0:
                pulse_start = time.time()

            # Wait for the echo pin to go LOW
            while gpio.input(self.echo) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start

            if unit == "cm":
                distance = pulse_duration * self.const_cm
            elif unit == "in":
                distance = pulse_duration * self.const_in
            elif unit == "ft":
                distance = pulse_duration * self.const_ft

            acc += distance
            count += 1

        acc = round(acc / samples, 2)
        return acc


    def move_servo(self, pulsewidth):
        duty_cycle = pulsewidth / 1000.0 * 100 / 20.0
        self.pwm.ChangeDutyCycle(duty_cycle)

    def sweep(self, samples, direction):
        distances = []
        if direction == "left":
            start_pw = 2500
            end_pw = 1500
            step = -5
        elif direction == "right":
            start_pw = 1450
            end_pw = 500
            step = -5
        for pulsewidth in range(start_pw, end_pw, step):
            self.move_servo(pulsewidth)
            time.sleep(0.01)
        for _ in range(samples):
            distance = self.measure(5, "cm")
            distances.append(distance)
            time.sleep(0.01)
        return distances



