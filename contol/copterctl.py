import struct
import serial
import time
import pygame
import crc8dallas
from pygame.locals import *


class App:
    def __init__(self):
        pygame.init()

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
            baudrate=115200
        )
        self.serial.isOpen()
        time.sleep(5)
        print("serial ready")


    # convert range
    def range_convert(self, value, old_min, old_max, new_min, new_max):
        return ( (value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min


    # send data to dongle
    def send_data(self, t, a, e, r):
        msg_d = struct.pack("=HHHH", t, a, e, r)
        checksum = crc8dallas.calc(msg_d)
        msg = struct.pack("=HHHHB", t, a, e, r, checksum)
        #print(msg)
        self.serial.write(msg)


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

            throttle = int( self.range_convert(self.my_joystick.get_axis(4),-1,1,0,1000) )+1000;
            elevator = int( self.range_convert(self.my_joystick.get_axis(1),-1,1,0,1000) )+1000;
            aileron = int( self.range_convert(self.my_joystick.get_axis(0),-1,1,0,1000) )+1000;


            #print("{0}\t{1}\t{2}".format(throttle,elevator,aileron))
            #print(throttle)

            self.send_data(throttle,aileron,elevator,1500)
            #pygame.time.wait(5)
            res=self.serial.readline();
            print(res);
            pygame.time.wait(200)



app = App()
app.main()
