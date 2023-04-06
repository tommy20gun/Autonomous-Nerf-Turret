"""!
@file encoder.py
This file contains code for Lab 1. Contains a class for encoder reading and setup.

@author Eric Qian, Callan Hill, Tommy Xu
@date 1-Feb-2023
"""
import pyb


class EncoderReader:
    """!
    @brief This class implements an encoder driver for an ME405 kit.
    """
    def __init__(self, pin1, pin2, countTimer, interruptTimer):
        """!
        Initializes the encoder reader by setting up the pins and timers.
        @param pin1 The pin number of the first encoder pin.
        @param pin2 The pin number of the second encoder pin.
        @param countTimer The timer number to use for counting encoder pulses.
        @param interruptTimer The timer number to use for updating the position traveled.
        """
        ## The pin number of the first encoder pin.
        self.pinIn1 = pyb.Pin(pin1, pyb.Pin.IN)
        ## The pin number of the second encoder pin.
        self.pinIn2 = pyb.Pin(pin2, pyb.Pin.IN)
        ## The timer number to use for counting encoder pulses.
        self.countTimer = pyb.Timer(countTimer, prescaler=0, period=0xFFFF)
        ## The timer number to use for updating the position traveled.
        self.interruptTimer = pyb.Timer(interruptTimer, freq=500)
        ## Encoder Timer channel 1.
        self.ch1 = self.countTimer.channel(1, pyb.Timer.ENC_AB, pin=self.pinIn1)
        ## Encoder Timer channel 2.
        self.ch2 = self.countTimer.channel(2, pyb.Timer.ENC_AB, pin=self.pinIn2)
        ## The previous position of the encoder.
        self.oldcount = 0
        ## The current position of the encoder.
        self.position = 0
        # configure interrupt callback.
        self.interruptTimer.callback(self.read)

    def read(self, _timer):
        """!
        Reads the encoder and updates the position.
        @param _timer The timer that triggered the interrupt.
        """
        counter = self.countTimer.counter()
        delta = counter - self.oldcount
        self.oldcount = counter

        if delta > 65536 // 2:
            # underflow handling
            delta -= 65536
        elif delta < -(65536 // 2):
            # overflow handling
            delta += 65536
        self.position = delta + self.position
        #print(self.position)

    def zero(self):
        """!
        Zeros the encoder position.
        """
        self.position = 0


if __name__ == "__main__":
    import time
    encoder1 = EncoderReader(pyb.Pin.board.PB6, pyb.Pin.board.PB7, 4, 2)
    while True:
        print(f"ENCODER: {encoder1.position}")
        time.sleep(1)
        




