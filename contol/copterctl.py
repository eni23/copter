#/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import serial
import time
import pygame
import sys
import log
from pygame.locals import *

class App:
    def __init__(self):
        self.sensitivity = 80
        self.ticktime = 60
        self.flip_running=False
        self.flip_step=0
        self.limit_data = {};
        self.mode = 1;

        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self.joystick_names = []

        if pygame.joystick.get_count()==0:
            log.error("No joysticks found")
            sys.exit(1)

        log.debug("Using Joystick: {}".format(pygame.joystick.Joystick(0).get_name()))

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        log.info("Joystick initalized, press r2 to continue")
        val=0
        while val != -1.0:
            self.g_keys = pygame.event.get()
            val = self.joystick.get_axis(4)
            pygame.time.wait(20)
        log.info("Joystick nulled")

        # init usb serial dongle
        self.init_serial()


    # init serial port
    def init_serial(self):
        log.debug("Opening serial port")
        try:
            self.serial = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate=57600
            )
        except:
            log.error("Opening serial port failed")
            sys.exit(1)
        self.serial.isOpen()
        time.sleep(1)
        log.debug("Serial ready")
        log.info("Turn on the quadcopter now")
        r = self.serial.read(1)
        log.debug("Got response from dongle: {0}".format(r[0]))
        time.sleep(3)
        log.info("Ready to fly")


    def millis(self):
        return int(round(time.time() * 1000))

    def limit(self, id, every_ms ):
        now = self.millis()
        try:
            dbdata = self.limit_data[str(id)]
        except KeyError:
            self.limit_data[str(id)] = 0
            dbdata = 0
        if dbdata < (now - every_ms):
            self.limit_data[str(id)] = now
            return True
        else:
            return False

    # invert float number
    def invert_float(self, n):
        n *= -1;
        return n;

    # convert range
    def range_convert(self, value, old_min, old_max, new_min, new_max):
        return ( (value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min


    # send data to dongle
    def send_data(self, t, a, e, r, cmd):
        msg = struct.pack("=HHHHB", t, a, e, r, cmd)
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


            # default dongle cmd is 0
            cmd = 0

            # Sensitivity / mode setting
            b_hat = self.joystick.get_hat(0)
            if (b_hat[0] != 0):
                if ( self.limit(0, 180) ):
                    if (b_hat[0] == -1):
                        if self.mode > 1:
                            self.mode = self.mode - 1
                            cmd = self.mode + 1
                    else:
                        if self.mode < 3:
                            self.mode = self.mode + 1
                            cmd = self.mode + 1
                    log.info("Mode: {0}".format(self.mode))

            if (b_hat[1] != 0):
                if ( self.limit(0, 180) ):
                    if (b_hat[1] == -1):
                        if self.sensitivity > 1:
                            self.sensitivity = self.sensitivity - 1
                    else:
                        if self.sensitivity < 100:
                            self.sensitivity = self.sensitivity + 1
                    log.info("Sensitivity: {0}%".format(self.sensitivity))


            # flip functionality
            if self.joystick.get_button(1) and not self.flip_running:
                #log.info("flip")
                self.flip_running = True;
                flip_save = elevator
                flip_th_step = ( ( 2000 - flip_save ) / 20 )
            if self.flip_running:
                cmd=1
                fl_th=flip_save
                if (self.flip_step>10):
                    fl_th = int(flip_th_step * self.flip_step) + flip_save
                if self.flip_step>=20:
                    self.flip_running=False
                    self.flip_step=0
                self.flip_step+=1

            raw_t = self.joystick.get_axis(4)
            raw_r = self.joystick.get_axis(2)
            raw_e = self.invert_float( self.joystick.get_axis(1) )
            raw_a = self.joystick.get_axis(0)

            throttle = int( ( self.range_convert( raw_t , -1, 1, 0, 1000 ) / 100 ) * self.sensitivity ) + 1000
            rudder   = self.ppm_val( self.min_pct(raw_r, self.sensitivity) )
            # flip is running
            if cmd==1:
                elevator = fl_th
            else:
                elevator = self.ppm_val( self.min_pct(raw_e, self.sensitivity) )
            aileron  = self.ppm_val( self.min_pct(raw_a, self.sensitivity) )

            self.send_data(throttle,aileron,elevator,rudder,cmd)
            pygame.time.wait(5)


try:
    app = App()
    app.main()
except KeyboardInterrupt:
    sys.exit(0)
