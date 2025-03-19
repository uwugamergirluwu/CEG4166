#Import Libraries
from matplotlib.pylab import *
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.animation as animation
import time

class multiplePlots:
    def __init__(self, leftEncoderCount, rightEncoderCount,
                 sonarSensor, samples, xmax):
        self.leftEncoderCount = leftEncoderCount
        self.rightEncoderCount = rightEncoderCount
        self.sonarSensor = sonarSensor
        self.samples = samples
        self.xmax = xmax
        self.ymax = 200
		
	  #Define sampleTime to calculate the speed and the tf variable, which
        #represents 
	  #the end time of the speed measuring
        self.sampleTime = 1
        self.tf = time.time() + self.sampleTime

        # Sent for figure
        self.font = {'size'   : 9}
        matplotlib.rc('font', **self.font)

        # Setup figure and subplots
        self.f0 = figure(num = 0, figsize = (6, 4))
        self.f0.suptitle("Robot Motion Analysis", fontsize=12)
        self.ax01 = subplot2grid((3, 1), (0, 0))  # Distance vs Time
        self.ax02 = subplot2grid((3, 1), (1, 0))  # Wheel Ticks vs Time
        self.ax03 = subplot2grid((3, 1), (2, 0))  # Sonar Distance vs Time

        # Data Placeholders
        self.yp1=zeros(0)
        self.yv1=zeros(0)
        self.yp2=zeros(0)
        self.yv2=zeros(0)
        self.t=zeros(0)
        self.leftWheelTicks = zeros(0)
        self.rightWheelTicks = zeros(0)
        self.sonarDist = zeros(0)


        # set plots (removed speed plots)
        self.p011, = self.ax01.plot(self.t, self.yp1, 'b-', label="LeftWheel")
        self.p012, = self.ax01.plot(self.t, self.yp2, 'g-', label="RightWheel")
        self.p021, = self.ax02.plot(self.t, self.leftWheelTicks, 'r-', label="Left Wheel Ticks")
        self.p022, = self.ax02.plot(self.t, self.rightWheelTicks, 'y-', label="Right Wheel Ticks")
        self.p031, = self.ax03.plot(self.t, self.sonarDist, 'm-', label="Sonar Distance")

        # set legends
        self.ax01.legend([self.p011, self.p012], [self.p011.get_label(), self.p012.get_label()])
        self.ax02.legend([self.p021, self.p022], [self.p021.get_label(), self.p022.get_label()])
        self.ax03.legend([self.p031], [self.p031.get_label()])

        # Data Update
        self.xmin = 0.0
        self.x = 0.0

        # Set titles of subplots
        self.ax01.set_title('Distance vs Time')
        self.ax02.set_title('Wheel Ticks vs Time')
        self.ax03.set_title('Sonar Distance vs Time')

        # set y-limits
        self.ax01.set_ylim(0, 200)
        self.ax02.set_ylim(0, 500)
        self.ax03.set_ylim(0, 100)

        for ax in [self.ax01, self.ax02, self.ax03]:
            ax.set_xlim(0, 5.0)
            ax.set_xlabel("t")
            ax.grid(True)

        # set label names
        self.ax01.set_xlabel("t")
        self.ax01.set_ylabel("Distance")
        self.ax02.set_xlabel("t")
        self.ax02.set_ylabel("Ticks")
        self.ax03.set_xlabel("t")
        self.ax03.set_ylabel("Distance")

	  #start the variables with 0
        self.totLeftDist = 0
        self.totRightDist = 0
        
        self.leftSpeed = 0
        self.rightSpeed = 0
        
        self.ini_pos_left = 0
        self.ini_pos_right = 0
        self.x = 0.0
	

    def updateWheelTicks(self):
        self.leftWheelTicksCount = self.leftEncoderCount.getTicks()
        self.rightWheelTicksCount = self.rightEncoderCount.getTicks()
        return self.leftWheelTicksCount, self.rightWheelTicksCount

    def sonarDistance(self):
        return self.sonarSensor.measure()


    # measure the speed of the robot
    def getSpeed(self):
        if (time.time() >= self.tf):
            self.tf = time.time() + self.sampleTime
            self.leftSpeed = (self.leftEncoderCount.getTotalDistance() - self.ini_pos_left)/self.sampleTime
            self.rightSpeed = (self.rightEncoderCount.getTotalDistance() - self.ini_pos_right)/self.sampleTime
            self.ini_pos_left = self.leftEncoderCount.getTotalDistance()
            self.ini_pos_right = self.rightEncoderCount.getTotalDistance()

    def teste(self):
        return self.xmax, self.yp1

    def updateData(self):
        self.totLeftDist = self.leftEncoderCount.getTotalDistance()
        self.totRightDist = self.rightEncoderCount.getTotalDistance()

        self.getSpeed()

        self.yp1 = append(self.yp1, self.totLeftDist)
        self.yp2 = append(self.yp2, self.totRightDist)
        self.t = append(self.t, self.x)

        leftWheelTicks, rightWheelTicks = self.updateWheelTicks()
        self.leftWheelTicks = append(self.leftWheelTicks, leftWheelTicks)  # Left wheel ticks
        self.rightWheelTicks = append(self.rightWheelTicks, rightWheelTicks)  # Right wheel ticks
        
        self.sonarDist = append(self.sonarDist, self.sonarSensor.getDistance())

        self.x += 0.3

        self.p011.set_data(self.t, self.yp1)
        self.p012.set_data(self.t, self.yp2)
        self.p031.set_data(self.t, self.wheelTicks)
        self.p041.set_data(self.t, self.sonarDist)

        for ax, data in zip([self.ax01, self.ax02, self.ax03],
                            [self.yp1, self.wheelTicks, self.sonarDist]):
            if data[-1] >= self.ymax - 40:
                ax.set_ylim(data[-1] - self.ymax + 40, data[-1] + 40)
            if self.x >= self.xmax - 1.0:
                ax.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)


