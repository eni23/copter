import struct
import serial
import time
import pygame
import crc8dallas
import sys
import log
from pygame.locals import *


class App:
    def __init__(self):
        self.sensitivity = 80
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self.joystick_names = []
        for i in range(0, pygame.joystick.get_count()):
            self.joystick_names.append(pygame.joystick.Joystick(i).get_name())
        log.debug("Using Joystick: " + self.joystick_names[0])

        if (len(self.joystick_names) > 0):
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            log.info("Joystick initalized, press r2 to continue")
            val=0
            while val != -1.0:
                self.g_keys = pygame.event.get()
                val = self.joystick.get_axis(4)
                pygame.time.wait(20)
            log.info("Joystick calibrated")

        # init usb serial dongle
        self.init_serial()


    # init serial port
    def init_serial(self):
        log.debug("Opening serial port")
        self.serial = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=57600
        )
        self.serial.isOpen()
        time.sleep(1)
        log.debug("Serial ready")
        log.info("Turn on the quadcopter now")
        r = self.serial.read(1)
        log.debug("Got response from dongle: {0}".format(r[0]))
        time.sleep(5)
        log.info("Ready to fly")


    # invert float number
    def invert_float(self, n):
        n *= -1;
        return n;

    # convert range
    def range_convert(self, value, old_min, old_max, new_min, new_max):
        return ( (value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min


    # send data to dongle
    def send_data(self, t, a, e, r):
        #msg_d = struct.pack("=HHHH", t, a, e, r)
        #checksum = crc8dallas.calc(msg_d)
        msg = struct.pack("=HHHHB", t, a, e, r, 0)
        self.serial.write(msg)


    def min_th(self, value, num):
        if value > 0:
            return value - num
        else:
            return value + num

    def min_pct(self, value, amount):
        return value * (amount / 100)

    def ppm_val(self, value):
        return int( self.range_convert(value,-1,1,0,1000) + 1000 )


    # main loop
    def main(self):
        pt=0
        while (True):

            self.g_keys = pygame.event.get()

            for event in self.g_keys:
                if (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.quit()
                    return
                elif (event.type == QUIT):
                    self.quit()
                    return

            if (self.joystick.get_button(4)):
                self.sensitivity = self.sensitivity - 1;
                log.info("Sensitivity: {0}%".format(self.sensitivity))
            if (self.joystick.get_button(5)):
                self.sensitivity = self.sensitivity + 1;
                log.info("Sensitivity: {0}%".format(self.sensitivity))

            raw_t = self.joystick.get_axis(4)
            raw_r = self.joystick.get_axis(2)
            raw_e = self.invert_float( self.joystick.get_axis(1) )
            raw_a = self.joystick.get_axis(0)

            throttle = self.ppm_val( raw_t )
            rudder   = self.ppm_val( self.min_pct(raw_r, self.sensitivity) )
            elevator = self.ppm_val( self.min_pct(raw_e, self.sensitivity) )
            aileron  = self.ppm_val( self.min_pct(raw_a, self.sensitivity) )

            #log.debug("{0}\t{1}\t{2}\t{3}".format(throttle,elevator,aileron,rudder))
            self.send_data(throttle,aileron,elevator,rudder)
            pygame.time.wait(60)


app = App()
app.main()
