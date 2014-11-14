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
ser = serial.Serial('/dev/ttyACM0', 115200)

# Pull JSON file for the StopID# 3010131 (12 Trikk)
try:
	turl = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010131"
	tdata = json.load(urllib2.urlopen(turl))
	j = 0
	sentrumtimes = list()
	majortimes = list()
	while j < len(tdata):
		if tdata[j][u'DirectionRef'] == '1':
			sentrumtimes.append(tdata[j][u'ExpectedArrivalTime'])
		elif tdata[j][u'DirectionRef'] == '2':
			majortimes.append(tdata[j][u'ExpectedArrivalTime'])
		j = j + 1

except:
	ser.write(b'\xFE')
	ser.write(b'\x58')
	ser.write("Connect Error")
	sys.exit()
	

# Collect current time
current = datetime.datetime.fromtimestamp(int(time.time())) ## Current time

for x in range(0, 3):

	## Wipe and Start First Line -- with catchall exception
	try:
		st1 = datetime.datetime.fromtimestamp(int(sentrumtimes[0][6:16])) ## First sentrum time tuple
		stfirst = dateutil.relativedelta.relativedelta (st1, current) ## First diff
		ser.write(b'\xFE')
		ser.write(b'\x58')
		ser.write("Sentrum:    %dm" % stfirst.minutes)
	except: 
		ser.write(b'\xFE')
		ser.write(b'\x58')
		ser.write("Sentrum:   NA")


	## Second Line -- with late night N/A exception
	try:
		st2 = datetime.datetime.fromtimestamp(int(sentrumtimes[1][6:16])) ## First sentrum time tuple
		stsecond = dateutil.relativedelta.relativedelta (st2, current) ## First diff
		ser.write(b'\xFE')
		ser.write(b'\x47')
		ser.write("\x01")
		ser.write("\x02")
		ser.write("Sentrum:    %dm" % stsecond.minutes)
	except:
		ser.write(b'\xFE')
		ser.write(b'\x47')
		ser.write("\x01")
		ser.write("\x02")
		ser.write("Sentrum:   NA")


	## Wait (Use with "watch -n 7" bash script)
	time.sleep(5)


	## Wipe and Start First Line -- with catch-all exception
	try:
		mt1 = datetime.datetime.fromtimestamp(int(majortimes[0][6:16])) ## First majorstuen time tuple
		mtfirst = dateutil.relativedelta.relativedelta (mt1, current) ## First diff
		ser.write(b'\xFE')
		ser.write(b'\x58')
		ser.write("Majorstuen: %dm" % mtfirst.minutes)
	except:
		ser.write(b'\xFE')
		ser.write(b'\x58')
		ser.write("Majorstuen:   NA")

	## Second Line -- with late night N/A exception
	try:
		mt2 = datetime.datetime.fromtimestamp(int(majortimes[1][6:16])) ## Second majorstuen time tuple
		mtsecond = dateutil.relativedelta.relativedelta (mt2, current) ## Second diff
		ser.write(b'\xFE')
		ser.write(b'\x47')
		ser.write("\x01")
		ser.write("\x02")
		ser.write("Majorstuen: %dm" % mtsecond.minutes)
	except:
		ser.write(b'\xFE')
		ser.write(b'\x47')
		ser.write("\x01")
		ser.write("\x02")
		ser.write("Majorstuen:  NA")


