#!/usr/bin/python3
##
# Two line sign that shows two departures for two lines simultaneously
# and outputs specifically to a 16x2 character display.
# Sample calls given for Sofienberg Bus and Tram departures going
# downtown.
# https://reisapi.ruter.no/StopVisit/GetDepartures/3010533?transporttypes=Bus,Tram&linenames=17,31
## Sofienberg = 3010533
# Vehicle = Metro/Tram/Bus/Train or combos of "Tram,Bus"
## LineNos = 31 or 17 or "31,17"

from lcdbackpack import LcdBackpack
import urllib.request
from collections import defaultdict
from urllib.error import URLError
import time
import json
from datetime import datetime, timezone
import dateutil.relativedelta
from dateutil.parser import parse
from time import sleep

# timeGrabber used once per update, calls all applicable for one stop
# One stopID and multiple vehicles and line numbers possible
# A couple shortened keys to keep it simple
MVJ = 'MonitoredVehicleJourney'
EAT = 'ExpectedArrivalTime'
debug = False

lcdscreen = LcdBackpack('/dev/ttyACM0', 115200)
lcdscreen.connect()
lcdscreen.clear()
lcdscreen.write("tramtimer v.03")

# Prints diagnostic data about the information taken for 17/31


def dataDebug(extract):
    print("URLDATA LENGTH " + str(len(extract)))
    print("Headways dict entries for")
    print("17:")
    print(extract['17'])
    print("31:")
    print(extract['31'])


def timeGrabber(stopID, vehicleTypes, lineNos, direction):

    grabbedDict = defaultdict(list)

    url = "http://reisapi.ruter.no/StopVisit/GetDepartures/" + str(stopID)
    url = url + "?transporttypes=" + vehicleTypes
    url = url + "&linenames=" + lineNos

    urlRequest = urllib.request.urlopen(url)
    urlData = json.loads(urlRequest.read().decode())

    i = 0
    while i < len(urlData):
        if (urlData[i][MVJ]['DirectionRef'] == str(2)):
            grabbedDict[urlData[i][MVJ]['LineRef']].append(
                parse(urlData[i][MVJ]['MonitoredCall'][EAT]))
        i += 1
    return grabbedDict


def mainloop():
    # Set current time
    current = datetime.now(timezone.utc)

    # Assign trains to track for each line
    try:
        headways = timeGrabber(3010533, "Bus,Tram", "31,17", 2)
    except URLError as e:
        if hasattr(e, 'reason'):
            print("Failed to reach server.")
            print("Reason: ", e.reason)
            lcdscreen.clear()
            lcdscreen.write("NO CONNECT")
            time.sleep(10)
        elif hasattr(e, 'code'):
            print("The server could not fill request.")
            print("Error code: ", e.code)
            lcdscreen.clear()
            lcdscreen.write("ERR: ", e.code)
            time.sleep(10)
    except ConnectionResetError as e:
        print("CAUGHT ConnectionResetError")
        # print("Code: ", e.code) CRE's have no attr 'code'
        lcdscreen.clear()
        lcdscreen.write("ConnResetError")
        time.sleep(10)
    except ValueError as e:
        print("VALUE ERROR")
        lcdscreen.clear()
        lcdscreen.write("VALERROR")
        time.sleep(10)
    except:
        print("UNEXPECTED ERROR:", sys.exc_info()[0])
        raise

    else:
        if (debug):
            dataDebug(headways)

        top = headways['17']
        bottom = headways['31']

        # Write "top" list
        if len(top) == 0:
            topcombo = "17:   n/a"
        if len(top) > 0:
            toptuple = dateutil.relativedelta.relativedelta(top[0], current)
            topcombo = "17: " + str(toptuple.minutes) + 'm '
        if len(top) > 1:
            toptuple = dateutil.relativedelta.relativedelta(top[1], current)
            topcombo += str(toptuple.minutes) + 'm '
        if len(top) > 2:
            toptuple = dateutil.relativedelta.relativedelta(top[2], current)
            topcombo += str(toptuple.minutes) + 'm'

        if (debug):
            print(topcombo)

        lcdscreen.clear()
        lcdscreen.write(topcombo)

        # Write 'bottom' list
        if len(bottom) == 0:
            bottomcombo = "31:   n/a"
        if len(bottom) > 0:
            bottomtuple = dateutil.relativedelta.relativedelta(
                bottom[0], current)
            bottomcombo = "31: " + str(bottomtuple.minutes) + 'm '
        if len(bottom) > 1:
            bottomtuple = dateutil.relativedelta.relativedelta(
                bottom[1], current)
            bottomcombo += str(bottomtuple.minutes) + 'm '
        if len(bottom) > 2:
            bottomtuple = dateutil.relativedelta.relativedelta(
                bottom[2], current)
            bottomcombo += str(bottomtuple.minutes) + 'm'

        if (debug):
            print(bottomcombo)
        lcdscreen.set_cursor_position(1, 2)
        lcdscreen.write(bottomcombo)

        time.sleep(20)


while True:
    mainloop()
