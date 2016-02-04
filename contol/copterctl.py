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
        self.ticktime = 60
        self.flip_running=False
        self.flip_step=0
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
    def send_data(self, t, a, e, r, f):
        msg = struct.pack("=HHHHH", t, a, e, r, f)
        self.serial.write(msg)


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
            '''
            if (self.joystick.get_button(4)):
                self.ticktime = self.ticktime - 1;
                log.info("Tick time: {0}".format(self.ticktime))
            if (self.joystick.get_button(5)):
                self.ticktime = self.ticktime + 1;
                log.info("Tick time: {0}".format(self.ticktime))
            '''


            # flip functionality
            if self.joystick.get_button(1) and not self.flip_running:
                log.info("flip")
                self.flip_running = True;
                flip_save = elevator
                flip_th_step = ( ( 2000 - flip_save ) / 20 )
            if self.flip_running:
                flip=2000
                fl_th=flip_save
                if (self.flip_step>10):
                    fl_th = int(flip_th_step * self.flip_step) + flip_save
                if self.flip_step>=20:
                    self.flip_running=False
                    self.flip_step=0
                self.flip_step+=1
            else:
                flip=1000

            raw_t = self.joystick.get_axis(4)
            raw_r = self.joystick.get_axis(2)
            raw_e = self.invert_float( self.joystick.get_axis(1) )
            raw_a = self.joystick.get_axis(0)

            throttle = int( ( self.range_convert( raw_t , -1, 1, 0, 1000 ) / 100 ) * self.sensitivity ) + 1000
            #throttle = self.ppm_val( raw_t )
            rudder   = self.ppm_val( self.min_pct(raw_r, self.sensitivity) )
            if self.flip_running:
                elevator = fl_th
            else:
                elevator = self.ppm_val( self.min_pct(raw_e, self.sensitivity) )
            aileron  = self.ppm_val( self.min_pct(raw_a, self.sensitivity) )

            #print(raw_t, throttle_sens)
            #log.debug("{0}\t{1}\t{2}\t{3}".format(throttle,elevator,aileron,rudder))
            self.send_data(throttle,aileron,elevator,rudder,flip)
            pygame.time.wait(5)


app = App()
app.main()
