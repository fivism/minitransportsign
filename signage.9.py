#!/usr/bin/python3
##
## Two line sign that shows two departures for two lines simultaneously 
## and outputs specifically to a 16x2 character display.
##
## Michael Fivis

import json
import os
import glob
import sys
import serial 
import urllib2
import time
import datetime 
import dateutil.relativedelta
from time import sleep


## KpaBap's print-replacement and log block
def print(s, **kwargs):
    __builtins__.print(time.strftime("[%b %d %H:%M:%S] ") + s, **kwargs)

class simpleLogger():

    def __init__(self,logfile):
        self.logfile = logfile
        open(logfile,"w").write("")

    def write(self,logtext):
        logfile = open(self.logfile,"a")
        logfile.write(logtext)
        logfile.flush()
        logfile.close()
        return 0

    def flush(self):
        return 0 

def mainloop():
    sys.stdout = simpleLogger("/home/pi/bike/lcd.log")
    sys.stderr = simpleLogger("/home/pi/bike/lcd-err.log")
    ser = serial.Serial('/dev/ttyACM0', 115200)

    url11 = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010511"
    url17 = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010531"
