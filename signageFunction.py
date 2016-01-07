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
import threading
from time import sleep


## This function we feed the Ruter StopID, line and direction
## It should then return as many time tuples as are available as a list

def timeGrabber(stopID, line, direction):

	grabbedList = list()
	url = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/" + str(stopID)
	urlRequest = urllib.request.urlopen(url)
	urlData = json.loads(urlRequest.read().decode())
	
	i = 0
	while i < len(urlData):
		if (urlData[i]['DirectionRef'] == str(direction) and urlData[i]['LineRef'] == str(line)):
			grabbedList.append(urlData[i]['ExpectedArrivalTime'])
		i = i + 1
	return grabbedList
	
	
def mainloop():
    # Start threading self destruct
    t = threading.Timer(15, mainloop)
    t.start()

    ser = serial.Serial('/dev/ttyACM0', 115200)
    
    ## Set current time
    current = datetime.datetime.fromtimestamp(int(time.time())) 

## For example--
## "17 nord" = 3010531, 17, 1
## "17 vest" = 3010531, 17, 2

## Assign trains to track for each line
    top = timeGrabber(3010531,17,2) 
    bottom = timeGrabber(3010531,17,1)

## Write "top" list
    if len(top) == 0: 
        topcombo = "17 Vest:   n/a"
    elif len(top) == 1:
        top1 = datetime.datetime.fromtimestamp(int(top[0][6:16]))
        top1tuple = dateutil.relativedelta.relativedelta (top1, current) 
        topcombo = "17 Vest: " + str(top1tuple.minutes) + 'm'
    elif len(top) > 1:
        top1 = datetime.datetime.fromtimestamp(int(top[0][6:16]))
        top1tuple = dateutil.relativedelta.relativedelta (top1, current) 
        top2 = datetime.datetime.fromtimestamp(int(top[1][6:16]))
        top2tuple = dateutil.relativedelta.relativedelta (top2, current)
        topcombo = "17 Vest: " + str(top1tuple.minutes) + 'm ' + str(top2tuple.minutes) + 'm'
    else:
        topcombo = "17 Vest:   n/a"   

	## Cast as bytes
    topcombob = topcombo.encode()

    ser.write(b'\xFE')
    ser.write(b'\x58')
    ser.write(topcombob)

## Write "bottom" list
    if len(bottom) == 0: 
        bottomcombo = "17 Nord:   n/a"
    elif len(bottom) == 1:
        bottom1 = datetime.datetime.fromtimestamp(int(bottom[0][6:16]))
        bottom1tuple = dateutil.relativedelta.relativedelta (bottom1, current) 
        bottomcombo = "17 Nord: " + str(bottom1tuple.minutes) + 'm'
    elif len(bottom) > 1: 
        bottom1 = datetime.datetime.fromtimestamp(int(bottom[0][6:16]))
        bottom1tuple = dateutil.relativedelta.relativedelta (bottom1, current) 
        bottom2 = datetime.datetime.fromtimestamp(int(bottom[1][6:16]))
        bottom2tuple = dateutil.relativedelta.relativedelta (bottom2, current)
        bottomcombo = "17 Nord: " + str(bottom1tuple.minutes) + 'm ' + str(bottom2tuple.minutes) + 'm'
    else:
        bottomcombo = "17 Nord:   n/a"  

    bottomcombob = bottomcombo.encode()

    ser.write(b'\xFE')
    ser.write(b'\x47')
    ser.write(b'\x01')
    ser.write(b'\x02')
    ser.write(bottomcombob)

	# time.sleep(15)

mainloop()
