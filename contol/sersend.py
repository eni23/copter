#/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import serial
import time

PPM_MIN=1000
PPM_SAFE_THROTTLE=1050
PPM_MID=1500
PPM_MAX=2000


def send_data(ser, t, a, e, r):
    msg = struct.pack("=HHHH", t, a, e, r)
    ser.write(msg)


print("opening serial")
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200
)
ser.isOpen()
time.sleep(5)
print("serial ready")
while True:
    thr = input("throttle: ")
    try:
        th = int(thr)
    except:
        th=1050;
        
    send_data(ser,th,PPM_MID,PPM_MID,PPM_MID);