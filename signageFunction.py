#!/usr/bin/python2
##
## Two line sign that shows two departures for two lines simultaneously 
## and outputs specifically to a 16x2 character display.

import json
import os
import glob
import sys
from lcdbackpack import LcdBackpack
import urllib.request
from collections import defaultdict
#from urllib2 import urlopen
import urllib.error
import time
from datetime import datetime, timezone 
import dateutil.relativedelta
from dateutil.parser import parse
import threading
from time import sleep

# timeGrabber used once per update, calls all applicable for one stop  
# One stopID and multiple vehicles and line numbers possible

MVJ = 'MonitoredVehicleJourney'
EAT = 'ExpectedArrivalTime'
debug = False

lcdscreen = LcdBackpack('/dev/ttyACM0', 115200)
lcdscreen.connect()
lcdscreen.clear()
lcdscreen.write("tramtimer v.02") 

# Prints diagnostic data about the information taken for 17/31
def dataDebug(extract):
    print("URLDATA LENGTH " + str(len(extract)))
    print("Headways dict entries for")
    print("17:")
    print(extract['17'])
    print("31:")
    print(extract['31'])

def timeGrabber(stopID, vehicleTypes, lineNos, direction):
    # Sofienberg = 3010533 
    # Vehicle = Metro/Tram/Bus/Train or combos of "Tram,Bus"
    # LineNos = 31 or 17 or "31,17"

    # https://reisapi.ruter.no/StopVisit/GetDepartures/3010533?transporttypes=Bus&linenames=31
    # https://reisapi.ruter.no/StopVisit/GetDepartures/3010533?transporttypes=Tram&linenames=17
    # We want direction = 2 for both I believe
    grabbedDict = defaultdict(list)
    
    url = "http://reisapi.ruter.no/StopVisit/GetDepartures/" + str(stopID)
    url = url + "?transporttypes=" + vehicleTypes   
    url = url + "&linenames=" + lineNos

	# url = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/" + str(stopID)
    urlRequest = urllib.request.urlopen(url)
    urlData = json.loads(urlRequest.read().decode())
    
    i = 0
    while i < len(urlData):    
        if (urlData[i][MVJ]['DirectionRef'] == str(2)):
            grabbedDict[urlData[i][MVJ]['LineRef']].append(parse(urlData[i][MVJ]['MonitoredCall'][EAT]))
        i += 1
    return grabbedDict

# lcdbackpack.disconnect() should be used as emergency break 
def mainloop():
    # Start threading self destruct
    # t = threading.Timer(15, mainloop)
    # t.start()
    
    ## Set current time
    current = datetime.now(timezone.utc)
    ## Assign trains to track for each line
    # Gather headways for Sofienberg (SWITCH OUT FOR GENERIC CONST) 

    headways = timeGrabber(3010533,"Bus,Tram","31,17",2)

    if (debug): 
        dataDebug(headways)

    top = headways['17'] 
    bottom = headways['31']

## Write "top" list
    
    if len(top) == 0: 
        topcombo = "17:   n/a"
    elif len(top) == 1:
        top1tuple = dateutil.relativedelta.relativedelta(top[0], current) 
        topcombo = "17: " + str(top1tuple.minutes) + 'm'
    elif len(top) > 1:
        top1tuple = dateutil.relativedelta.relativedelta (top[0], current) 
        top2tuple = dateutil.relativedelta.relativedelta (top[1], current)
        topcombo = "17: " + str(top1tuple.minutes) + 'm ' + str(top2tuple.minutes) + 'm'
    else:
        topcombo = "17:   n/a"   

    print(topcombo)

	## Cast as bytes
    #topcombob = topcombo.encode()
    lcdscreen.clear()
    lcdscreen.write(topcombo)

    if len(bottom) == 0:
        bottomcombo = "31:   n/a"
    elif len(bottom) == 1:
        bottom1tuple = dateutil.relativedelta.relativedelta(bottom[0], current) 
        bottomcombo = "31: " + str(bottom1tuple.minutes) + 'm'
    elif len(bottom) > 1: 
        bottom1tuple = dateutil.relativedelta.relativedelta(bottom[0], current) 
        bottom2tuple = dateutil.relativedelta.relativedelta(bottom[1], current)
        bottomcombo = "31: " + str(bottom1tuple.minutes) + 'm ' + str(bottom2tuple.minutes) + 'm'
    else:
        bottomcombo = "31:   n/a"  

    print(bottomcombo)
    lcdscreen.set_cursor_position(1, 2)
    lcdscreen.write(bottomcombo)

    time.sleep(20)

while True:
    mainloop()
