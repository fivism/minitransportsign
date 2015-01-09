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
import urllib.request
import urllib.error
import time
import datetime 
import dateutil.relativedelta
import traceback
import threading
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
    # Start threading self destruct
    t = threading.Timer(15, mainloop)
    t.start()

    sys.stdout = simpleLogger("/home/pi/bike/lcd.log")
    sys.stderr = simpleLogger("/home/pi/bike/lcd-err.log")
    ser = serial.Serial('/dev/ttyACM0', 115200)
    
    nybruatimes = list()
    heimdalstimes = list()

    try:
        url11 = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010511"
        url17 = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010531"
        url11request = urllib.request.urlopen(url11)
        url17request = urllib.request.urlopen(url17)
        url11data = json.loads(url11request.read().decode())
        url17data = json.loads(url17request.read().decode())

        i = 0
        j = 0

        while i < len(url11data):
            if (url11data[i]['DirectionRef'] == '2' and url11data[i]['LineRef'] == '11'):
                nybruatimes.append(url11data[i]['ExpectedArrivalTime'])
            i = i + 1
        while j < len(url17data):
            if (url17data[j]['DirectionRef'] == '2' and url17data[j]['LineRef'] == '17'):
                heimdalstimes.append(url17data[j]['ExpectedArrivalTime'])
            j = j + 1

    except:
        ser.write(b'\xFE')
        ser.write(b'\x58')
        ser.write("Connect Error".encode())
        print(traceback.format_exc())

## Set current time
    current = datetime.datetime.fromtimestamp(int(time.time())) 


## Write first line 
    if len(heimdalstimes) == 0: 
        topcombo = "17 Vest:   n/a"
    elif len(heimdalstimes) == 1:
        top1 = datetime.datetime.fromtimestamp(int(heimdalstimes[0][6:16]))
        top1tuple = dateutil.relativedelta.relativedelta (top1, current) 
        topcombo = "17 Vest: " + str(top1tuple.minutes) + 'm'
    elif len(heimdalstimes) > 1:
        top1 = datetime.datetime.fromtimestamp(int(heimdalstimes[0][6:16]))
        top1tuple = dateutil.relativedelta.relativedelta (top1, current) 
        top2 = datetime.datetime.fromtimestamp(int(heimdalstimes[1][6:16]))
        top2tuple = dateutil.relativedelta.relativedelta (top2, current)
        topcombo = "17 Vest: " + str(top1tuple.minutes) + 'm ' + str(top2tuple.minutes) + 'm'
    else:
        topcombo = "17 Vest:   n/a"   

    ## Cast as bytes
    topcombob = topcombo.encode()

    ser.write(b'\xFE')
    ser.write(b'\x58')
    ser.write(topcombob)


    # except: 
    #     ser.write(b'\xFE')
    #     ser.write(b'\x58')
    #     ser.write("17 Vest:  N/A")
    #     print (traceback.format_exc())

## Write second line

    if len(nybruatimes) == 0: 
        bottomcombo = "11 Vest:   n/a"
    elif len(nybruatimes) == 1:
        bottom1 = datetime.datetime.fromtimestamp(int(nybruatimes[0][6:16]))
        bottom1tuple = dateutil.relativedelta.relativedelta (bottom1, current) 
        bottomcombo = "11 Vest: " + str(bottom1tuple.minutes) + 'm'
    elif len(nybruatimes) > 1: 
        bottom1 = datetime.datetime.fromtimestamp(int(nybruatimes[0][6:16]))
        bottom1tuple = dateutil.relativedelta.relativedelta (bottom1, current) 
        bottom2 = datetime.datetime.fromtimestamp(int(nybruatimes[1][6:16]))
        bottom2tuple = dateutil.relativedelta.relativedelta (bottom2, current)
        bottomcombo = "11 Vest: " + str(bottom1tuple.minutes) + 'm ' + str(bottom2tuple.minutes) + 'm'
    else:
        bottomcombo = "11 Vest:   n/a"  

    bottomcombob = bottomcombo.encode()

    ser.write(b'\xFE')
    ser.write(b'\x47')
    ser.write(b'\x01')
    ser.write(b'\x02')
    ser.write(bottomcombob)

    # except: 
    #     ser.write(b'\xFE')
    #     ser.write(b'\x47')
    #     ser.write("\x01")
    #     ser.write("\x02")
    #     ser.write("11 Vest:   N/A")
    #     print (traceback.format_exc())

    # time.sleep(15)

mainloop()
    # except:
    #     print (traceback.format_exc())
