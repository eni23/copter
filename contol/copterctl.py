import struct
import serial
import time
import pygame
import crc8dallas
from pygame.locals import *


class App:
    def __init__(self):
        pygame.init()
        self.last_t = 1000;
        self.last_a = 1500;
        self.last_e = 1500;
        self.last_r = 1500;

        pygame.joystick.init()
        self.my_joystick = None
        self.joystick_names = []
        for i in range(0, pygame.joystick.get_count()):
            self.joystick_names.append(pygame.joystick.Joystick(i).get_name())

        print(self.joystick_names)

        # By default, load the first available joystick.
        if (len(self.joystick_names) > 0):
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()

        # init usb serial dongle
        self.init_serial()


    # init serial port
    def init_serial(self):
        print("opening serial")
        self.serial = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=57600
        )
        self.serial.isOpen()
        time.sleep(1)
        #print("serial ready")
        print("wait for pairing")
        r = self.serial.read(1)
        time.sleep(10)
        print("ready 2 fly")

    def invert_float(self, n):
        n *= -1;
        return n;

    # convert range
    def range_convert(self, value, old_min, old_max, new_min, new_max):
        return ( (value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min


    # send data to dongle
    def send_data(self, t, a, e, r):
        msg_d = struct.pack("=HHHH", t, a, e, r)
        #checksum = crc8dallas.calc(msg_d)
        msg = struct.pack("=HHHHB", t, a, e, r, 0)
        #print(msg)
        #self.serial.flushOutput()
        self.serial.write(msg)



    def min_th(self, value, num):
        if value > 0:
            return value - num
        else:
            return value + num


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



            throttle = int( self.range_convert(self.my_joystick.get_axis(4),-1,1,0,1000) + 1000 )

            val_ele = self.invert_float(self.my_joystick.get_axis(1))
            val_aie = self.my_joystick.get_axis(0)

            elevator = int( self.range_convert( val_ele,-1,1,0,1000) + 1000 )
            aileron =  int( self.range_convert( val_aie,-1,1,0,1000) + 1000 )


            rudder = int(self.range_convert(self.my_joystick.get_axis(2),-1,1,0,1000) )+1000;

            '''
            change = False
            if (self.last_t != throttle):
                change = True
                self.last_t = throttle
            if (self.last_a != aileron):
                change = True
                self.last_a = aileron
            if (self.last_e != elevator):
                change = True
                self.last_e = elevator
            if (self.last_r != rudder):
                change = True
                self.last_r = rudder
            '''
            if (True):
                print("{0}\t{1}\t{2}\t{3}".format(throttle,elevator,aileron,rudder))
                #self.send_data(throttle,aileron,elevator,rudder)
                self.send_data(throttle,aileron,elevator,rudder)
                pygame.time.wait(70)


app = App()
app.main()
