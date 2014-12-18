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
    sys.stdout = simpleLogger("lcd.log")
    sys.stderr = simpleLogger("lcd-err.log")
    ser = serial.Serial('/dev/ttyACM0', 115200)
	
    while(1):

		try:
			turl = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010531"
			tdata = json.load(urllib2.urlopen(turl))
			j = 0

			sentrumtimes = list()
			while j < len(tdata):
				if (tdata[j][u'DirectionRef'] == '2' and tdata[j][u'LineRef'] == '17'):
			   	    sentrumtimes.append(tdata[j][u'ExpectedArrivalTime'])
				j = j + 1

		except:
			ser.write(b'\xFE')
			ser.write(b'\x58')
			ser.write("Connect Error")
			#sys.exit()
		
		current = datetime.datetime.fromtimestamp(int(time.time())) ## Current time

		## Wipe and Start First Line -- with catchall exception
		try:
			st1 = datetime.datetime.fromtimestamp(int(sentrumtimes[0][6:16])) ## First sentrum time tuple
			stfirst = dateutil.relativedelta.relativedelta (st1, current) ## First diff
			ser.write(b'\xFE')
			ser.write(b'\x58')
			ser.write("17 Sentrum:  %dm" % stfirst.minutes)
		except: 
			ser.write(b'\xFE')
			ser.write(b'\x58')
			ser.write("17 Sentrum:   NA")


		## Second Line -- with late night N/A exception
		try:
			st2 = datetime.datetime.fromtimestamp(int(sentrumtimes[1][6:16])) ## First sentrum time tuple
			stsecond = dateutil.relativedelta.relativedelta (st2, current) ## First diff
			ser.write(b'\xFE')
			ser.write(b'\x47')
			ser.write("\x01")
			ser.write("\x02")
			ser.write("17 Sentrum:  %dm" % stsecond.minutes)
		except:
			ser.write(b'\xFE')
			ser.write(b'\x47')
			ser.write("\x01")
			ser.write("\x02")
			ser.write("17 Sentrum:   NA")

		time.sleep(15)

while(1):
	mainloop()
