"""!
@file controller.py
This file contains code for a closed loop controller for the motor.
@author Eric Qian, Callan Hill, Tommy Xu
@date 9-Feb-2023
"""
import utime
import time
import pyb
class Controller:
    """!
    @brief This class implements a closed feedbackloop with the encoder reader and motor driver.
    This allows the motor to "know" where it is and change it's duty cycle based on its position
    """
    
    def __init__ (self, kP, initialSetPoint):
        """!
        @brief Initializes the controller by obtaining a kP and initialset point.
        @param kP The proportionality constant of the controls.
        @param initialSetPoint The position where the user desires the motor to be.
        """
        self.kP = kP
        self.setPoint = initialSetPoint
        ## The uart object is created, allowing for uart communcation through the ST-link. Plotos are made on serialParser.py
        self.u2 = pyb.UART(2,baudrate=115200)
        ## The time at the start of the program. This will be subtracted from a timer later in the program to get the time difference.
        ## Essentially, this allows the program to zero its time.
        self.start = utime.ticks_ms()


    def run(self, currentPos):
        """! 
        @brief Implementation of the controls equation kP(thetafinal - thetainitial) = phi.
        @param currentPos The current position of the motor given by the encoder
        """
        error = (currentPos - self.setPoint)
        #returns actuation signal (dutycycle)
        return (self.kP * error)
        

    def set_point(self,num):
        """!
        @brief Changes the setpoint of the motor.
        @param num The signed integer that is the new setpoint.
        """
        self.setPoint = num
    
    def set_kP(self,num):
        """!
        @brief Changes the kP value of the controller
        @param num The signed integer than is the new kP value.
        """
        self.kP = num

    def dataOutput(self,currentPos):
        """!
        @brief Outputs the data in UTF-8 format through the ST-Link serially into the computer. serialParser.py reads this data.
        @param currentPos The current position of the encoder given by encoder reader. 
        """
        #self.u2.write("hi")
        self.u2.write(str(utime.ticks_ms() - self.start) + "," + str(currentPos) + "\r\n")
