## This seeks out the bicycle counts for 49 (Frognerveien) and 55 (Bygdoy) 
## from the most recent scrape in /scrapes
##
##
## Ideally in the future it will query a db where the scrapes are collected
##

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

## Initialize serial target


# Copied print and logging class from KpaBap's script

class simpleLogger():
    
    def __init__(self,logfile):
        self.logfile = logfile
        open(logfile,"w").write("") ##clear out any previous contents
    
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
	

    try:
		url11 = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010511"
		url17 = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010531"
		
		url11data = json.load(urllib2.urlopen(url11))
		url17data = json.load(urllib2.urlopen(url17))
		i = 0
		j = 0

		nybruatimes = list()
		heimdalstimes = list()

		while i < len(url11data):
			if (url11data[i][u'DirectionRef'] == '2' and url11data[i][u'LineRef'] == '11'):
		   	    nybruatimes.append(url11data[i][u'ExpectedArrivalTime'])
			i = i + 1
		while j < len(url17data):
			if (url17data[j][u'DirectionRef'] == '2' and url17data[j][u'LineRef'] == '17'):
		   	    heimdalstimes.append(url17data[j][u'ExpectedArrivalTime'])
			j = j + 1
    except:
	    ser.write(b'\xFE')
	    ser.write(b'\x58')
	    ser.write("Connect Error")
		#sys.exit()
	
	## Set current time
    current = datetime.datetime.fromtimestamp(int(time.time())) ## Current time

	## Wipe and Start First Line -- with catchall exception
    try:

    	if len(heimdalstimes) == 1:
            top1 = datetime.datetime.fromtimestamp(int(heimdalstimes[0][6:16]))
            top1tuple = dateutil.relativedelta.relativedelta (top1, current) ## First diff
            topcombo = str(top1tuple.minutes) + 'm '
    	else:
    	    top1 = datetime.datetime.fromtimestamp(int(heimdalstimes[0][6:16]))
            top1tuple = dateutil.relativedelta.relativedelta (top1, current) ## First diff 
            top2 = datetime.datetime.fromtimestamp(int(heimdalstimes[1][6:16]))
            top2tuple = dateutil.relativedelta.relativedelta (top2, current)
            topcombo = str(top1tuple.minutes) + 'm ' + str(top2tuple.minutes) + 'm'
		    
	    ser.write(b'\xFE')
	    ser.write(b'\x58')
	    ser.write("17 Vest: %s" % topcombo)

    except: 
	    ser.write(b'\xFE')
	    ser.write(b'\x58')
	    ser.write("17 Vest:  N/A")

	## Second Line 
    try:
    	print len(nybruatimes) ## Printout
    	if len(nybruatimes) == 1:
            bottom1 = datetime.datetime.fromtimestamp(int(nybruatimes[0][6:16]))
            bottom1tuple = dateutil.relativedelta.relativedelta (bottom1, current) 
            bottomcombo = str(bottom1tuple.minutes) + 'm '
    	else: 
            bottom1 = datetime.datetime.fromtimestamp(int(nybruatimes[0][6:16]))
            bottom1tuple = dateutil.relativedelta.relativedelta (bottom1, current) 
            bottom2 = datetime.datetime.fromtimestamp(int(nybruatimes[1][6:16]))
            bottom2tuple = dateutil.relativedelta.relativedelta (bottom2, current)
            bottomcombo = str(bottom1tuple.minutes) + 'm ' + str(bottom2tuple.minutes) + 'm'

	    ser.write(b'\xFE')
	    ser.write(b'\x47')
	    ser.write("\x01")
	    ser.write("\x02")
        ser.write("11 Vest: %s" % bottomcombo)

    except: 
	    ser.write(b'\xFE')
	    ser.write(b'\x47')
	    ser.write("\x01")
	    ser.write("\x02")
	    ser.write("11 Vest:  N/A")

    time.sleep(15)

while(1):
	mainloop()
