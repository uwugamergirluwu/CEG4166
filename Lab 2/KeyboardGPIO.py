import time
import sys
import tty
import termios


#merge into main after 



# Function to capture keyboard input
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

while True:
    # Capture keyboard input
    char = getch()
    
    if char == "w":
        print("Char W pressed")
    
    elif char == 'a':
        print("Char A")

    elif char == 'd':
        print("Char d")

    elif char == 's':
        print("Char s")
        
    # Exit program
    elif char == "e":
        exit()
