"""!
@file servodriver.py
This file contains a class for servo control and initialization.

@author Eric Qian, Callan Hill, Tommy Xu
@date 9-March-2023
"""
import pyb
import time

class ServoDriver:
    """!
    This class implements a servo driver.
    """

    def __init__(self, ch1pin, timer, af_mode):
        """!
        Creates a servo driver by initializing GPIO
        pins and turning off the motor for safety.
        @param ch1pin The pin number of the first channel
        @param timer The timer number to use for PWM
        """
        ## The pin number of motor pin A.
        self.pinOut1 = pyb.Pin(ch1pin, pyb.Pin.OUT_PP, alt=af_mode)  # output 1
        self.freq = 50
        self.min_time = 600
        self.max_time = 2400
        self.angle = 180
        self.time_range = self.max_time - self.min_time
        ## The timer number to use for PWM.
        self.tim = pyb.Timer(timer, freq=50, prescaler=79)
        ## The timer channel for the first PWM channel.
        self.ch1 = self.tim.channel(1, pyb.Timer.PWM, pin=self.pinOut1)
        # explicitly stop PWM at startup.
        self.ch1.pulse_width(0)
        print("Creating a servo driver")

    def set_duty(self, level):
        self.ch1.pulse_width(level)
    
    def set_degree(self, degree):
        print(f"Setting deg: {degree}")
        degree = degree % 360
        self.set_duty(self.min_time + self.time_range * degree // self.angle) 


if __name__ == "__main__":
    print("Testing servo driver")
    servo = ServoDriver(pyb.Pin.board.PC6, 3, pyb.Pin.AF2_TIM3)
    #servo.set_duty(50*110)
    servo.set_degree(210)
    #time.sleep(1)
    #for i in range(10):
    #    servo.set_degree(156)
    #    time.sleep(5)
    #    servo.set_degree(270)
     #   time.sleep(5)
        
        
        
    #for i in range(210, 90, -1):
    #    servo.set_degree(i)
        # 60 - minimum degree
        # 360 - maximum degree
        #print(i)
    #    time.sleep(0.2)
        
        # Kinematics - MAX TILT 170
        # Kinematics - MAX TILT 156
        
        
    #servo.set_degree(90)
    #time.sleep(1)
    #servo.set_duty(50*130)
    #servo.set_degree(120)
    #time.sleep(1000000)
    

