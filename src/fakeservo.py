"""!
@file fakeservo.py
This file abstracts a motor as a servo.

@author Eric Qian, Callan Hill, Tommy Xu
"""


import pyb
from encoder import EncoderReader
from controller import Controller
from motordriver import MotorDriver

class FakeServo:
    """! @brief This class implements a fake servo driver for a motor.
    This allows us to set the angle of our X axis and have it move to that angle."""

    def __init__(self):
        """! @brief Initializes the fake servo by creating a motor driver and encoder reader."""
        self.moe = MotorDriver(pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 5)
        self.encoder = EncoderReader(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4, 2)
    
    def reset(self):
        """! @brief Resets the encoder to 0."""
        self.encoder.zero()

    def run(self, angle):
        """! @brief Runs the motor to the given angle.
        @param angle The angle to move the motor to.
        """
        print(f"FAKESERVO: Setting angle: {angle}")
        kP = float(0.5)
        initialSetPoint = float(angle * 383)
        controller = Controller(kP, initialSetPoint)
        x_pos_ready = False
        while not x_pos_ready:
            controller.dataOutput(self.encoder.position)
            duty=controller.run(self.encoder.position)
            #print(f"ENCODER: {self.encoder.position}, DUTY: {duty}")
        #if controller.run(encoder.position) > 50:
        #    duty = 100
        #elif controller.run(encoder.position) < -50:
        #    duty = -100
        #else:
        #    duty = 0

        #duty = 100
        #turn_val = 60000
            self.moe.set_duty_cycle(duty)
            if (abs(self.encoder.position - initialSetPoint) < 100 and duty < 50):
                x_pos_ready = True
        #if (abs(encoder.position) >= turn_val):
        #    moe.set_duty_cycle(0)
        #    x_pos_ready = True
    
        self.moe.set_duty_cycle(0)

if __name__ == "__main__":
    import time
    fakeservo = FakeServo()
    while True:
        fakeservo.run(90)
        time.sleep(1)
        fakeservo.run(0)
        time.sleep(1)
        
