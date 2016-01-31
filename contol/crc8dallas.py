############################################
# This is for CRC-8 Maxim/Dallas Algorithm
# Improved with less variable and functions
# Supports both Python3.x and Python2.x
# Has append and check functions
# When standalone, can read from either arguments or stdin
# Writes to stdout cleaner
# http://gist.github.com/eaydin
############################################

import binascii
import sys
if sys.version_info[0] == 3:
    import codecs

def calc(incoming):
    check = 0
    for i in incoming:
        check = AddToCRC(i, check)
    return check

def AddToCRC(b, crc):
    if (b < 0):
        b += 256
    for i in range(8):
        odd = ((b^crc) & 1) == 1
        crc >>= 1
        b >>= 1
        if (odd):
            crc ^= 0x8C # this means crc ^= 140
    return crc

def check(incoming):
    """Returns True if CRC Outcome Is 0xx or 0x0"""
    result = calc(incoming)
    if result == "0x0" or result == "0x00":
        return True
    else:
        return False

def append(incoming):
    """Returns the Incoming message after appending it's CRC CheckSum"""
    result = calc(incoming).split('x')[1].zfill(2)
    return incoming + result
