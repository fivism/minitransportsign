## http://bysykkel-prod.appspot.com/json
## VERSION 2
## Collects snapshots of this third party json interpretation of the Oslo Bysykkel bikeshare status
## Creates CSV if none exists, and adds entries as single dated line.
##
## Michael Fivis 2014

import json
import urllib2
import time
import csv

# Collect current json into var 'data'
url = "http://bysykkel-prod.appspot.com/json"
data = json.load(urllib2.urlopen(url))

# Create, if doesn't exist, CSV file 
f = csv.writer(open("log.csv", "wb+"))

# Write column headers
# How to extract every station as a column...
# Pull out the json dict as a list of titles?

f.writerow(["date", "ID1_IN", "ID1_OUT"...])

for x in x:
	f.writerow([x["date"],
				x["ID1_IN"],
				x["ID1_OUT"],
				(...)

			])
# Introduce timestamped filename component
current_time = time.strftime("20%y%m%d%H%M00", time.localtime())
## OLD current_time = time.strftime("%d.%m.%y %H.%M", time.localtime())

output_name = 'scrapes/%s.txt' % current_time
output_file = open(output_name, "w")
json.dump(data, output_file)
output_file.close()


