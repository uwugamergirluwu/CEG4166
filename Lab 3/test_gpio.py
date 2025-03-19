import RPi.GPIO as gpio

gpio.setmode(gpio.BOARD)  # or gpio.BCM
gpio.setup(11, gpio.IN, pull_up_down=gpio.PUD_UP)

print("GPIO Setup Successful!")
gpio.cleanup()
