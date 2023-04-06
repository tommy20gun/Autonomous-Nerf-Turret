"""!
@file motordriver.py
This file contains code for Lab 1. Contains a class for motor control and initialization.

@author Eric Qian, Callan Hill, Tommy Xu
@date 1-Feb-2023
"""
import pyb


class MotorDriver:
    """!
    This class implements a motor driver for an ME405 kit.
    """

    def __init__(self, en_pin, ch1pin, ch2pin, timer):
        """!
        Creates a motor driver by initializing GPIO
        pins and turning off the motor for safety.
        @param en_pin The pin number of the enable pin
        @param ch1pin The pin number of the first channel
        @param ch2pin The pin number of the second channel
        @param timer The timer number to use for PWM
        """
        ## The pin number of motor pin A.
        self.pinOut1 = pyb.Pin(ch1pin, pyb.Pin.OUT_PP)  # output 1
        ## The pin number of motor pin B.
        self.pinOut2 = pyb.Pin(ch2pin, pyb.Pin.OUT_PP)  # output 2
        ## The pin number of the motor control enable pin.
        self.pinEn = pyb.Pin(
            en_pin, pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP
        )  # enable pinOUT with open drain control. Enables pull up resistor
        ## The timer number to use for PWM.
        self.tim = pyb.Timer(timer, freq=2000)
        ## The timer channel for the first PWM channel.
        self.ch1 = self.tim.channel(1, pyb.Timer.PWM, pin=self.pinOut1)
        ## The timer channel for the second PWM channel.
        self.ch2 = self.tim.channel(2, pyb.Timer.PWM, pin=self.pinOut2)
        # explicitly stop PWM at startup.
        self.ch1.pulse_width_percent(0)
        self.ch2.pulse_width_percent(0)
           # set motor enable pin to high.
        self.pinEn.high()
        print("Creating a motor driver")

    def set_duty_cycle(self, level):
        """!
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
               cycle of the voltage sent to the motor
        """
        if level <50 and level > -50:
            level = 0
        
        if level > 0:
            # forward direction
            self.pinEn.high()
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(level)
        elif level < 0:
            # reverse direction
            self.pinEn.high()
            self.ch1.pulse_width_percent(level * -1)
            self.ch2.pulse_width_percent(0)
        else:
            # stop motor
            self.pinEn.low()
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(0)
        #print("The logic of pinEN is ", self.pinEn.value())
        #print(f"Setting duty cycle to {level}")


if __name__ == "__main__":
    print("Testing motor driver")
    moe = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
    from encoder import EncoderReader
    from controller import Controller
    encoder = EncoderReader(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4, 2)
    kP = float(0.5)
    initialSetPoint = float(69000)
    controller = Controller(kP, initialSetPoint)
    x_pos_ready = False
    while not x_pos_ready:
        #print(f"ENCODER: {encoder.position}")
        controller.dataOutput(encoder.position)
        duty=controller.run(encoder.position)

        #if controller.run(encoder.position) > 50:
        #    duty = 100
        #elif controller.run(encoder.position) < -50:
        #    duty = -100
        #else:
        #    duty = 0

        #duty = 100
        #turn_val = 60000
        moe.set_duty_cycle(duty)
        if (abs(encoder.position - initialSetPoint) < 100 and duty < 50):
            x_pos_ready = True
        #if (abs(encoder.position) >= turn_val):
        #    moe.set_duty_cycle(0)
        #    x_pos_ready = True
    
    moe.set_duty_cycle(0)
    #moe.set_duty_cycle(0)
