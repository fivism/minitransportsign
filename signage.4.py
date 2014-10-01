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

##
## BIKESHARE READING SECTION
##

## Seek most recently created txt file
newest = max(glob.iglob('scrapes/*.txt'), key=os.path.getctime)

## Open this
json_data = open(newest)
jdata = json.load(json_data)

i = 0
while i < len(jdata):
	idvar = jdata[i][u'id']
	if idvar == 55:
			fiftyfive = jdata[i][u'bikesReady']
	elif idvar == 49:
			fortynine = jdata[i][u'bikesReady']
	i = i + 1


# Format as if for 16x2 display
# 

ser = serial.Serial('/dev/ttyACM0', 115200)

#Escape
ser.write(b'\xFE')

#clear screen and write 
ser.write(b'\x58')
ser.write("FROGNERVEIEN: %s   " % fortynine)
ser.write(b'\xFE')
ser.write(b'\x47')
ser.write("\x01")
ser.write("\x02")
ser.write("BYGDOY: %s" % fiftyfive)



##
## TRIKK SECTION
##

# Pull JSON file for the StopID# 3010131 (12 Trikk)
url = "http://reis.trafikanten.no/reisrest/realtime/getrealtimedata/3010131"
tdata = json.load(urllib2.urlopen(url))

j = 0
sentrumtimes = list()
majortimes = list()
while j < len(tdata):
	if tdata[j][u'DirectionRef'] == '1':
		print tdata[j][u'ExpectedArrivalTime']
		sentrumtimes.append(tdata[j][u'ExpectedArrivalTime'])
	elif tdata[j][u'DirectionRef'] == '2':
		print tdata[j][u'ExpectedArrivalTime']
		majortimes.append(tdata[j][u'ExpectedArrivalTime'])
	j = j + 1

# Calc readable diff between current unix time and next arrival
dt1 = datetime.datetime.fromtimestamp(int(time.time())) ## Current time
dt2 = datetime.datetime.fromtimestamp(int(sentrumtimes[0][6:16])) ## First time tuple
dt3 = datetime.datetime.fromtimestamp(int(sentrumtimes[1][6:16])) ## Second time tuple

rdfirst = dateutil.relativedelta.relativedelta (dt2, dt1) ## First diff
rdsecond = dateutil.relativedelta.relativedelta (dt3, dt1) ## Second diff


time.sleep(5)

ser.write(b'\x58')
ser.write("Til Sentrum: %d   " % rdfirst.minutes)
ser.write(b'\xFE')
ser.write(b'\x47')
ser.write("\x01")
ser.write("\x02")
ser.write("Neste: %d" % rdsecond.minutes)
#json_data.close()

