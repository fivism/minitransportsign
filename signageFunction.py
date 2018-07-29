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

from collections import defaultdict
import time
import json
from datetime import datetime, timezone
import dateutil.relativedelta
from dateutil.parser import parse
from time import sleep
import sys
import requests # https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad

LCD_ON = True  # for testing with/without serial LCD connection
DEBUG = False  # set extra output on

# Set required request header for Entur
headers = {'ET-Client-Name': 'fivism-avgangskilt'}
api_url = 'https://api.entur.org/journeyplanner/2.0/index/graphql'

# Relevant profiles dict TODO: Read this in as a separate file
ST_DICT = { "17-downtown": ['NSR:StopPlace:58190', 'NSR:Quay:104048', 'RUT:Line:17', '17'],
            "31-downtown": ['NSR:StopPlace:58190', 'NSR:Quay:11882', 'RUT:Line:31', '31'],
            "21-west": ['NSR:StopPlace:58189', 'NSR:Quay:11048', 'RUT:Line:21', '21']
}

# Selected profiles to display (Only 2 profiles on 16x2 display)
PROFILE_1 = ST_DICT['21-west']
PROFILE_2 = ST_DICT['31-downtown']

# Station and quays to seek
STATION_ID = PROFILE_1[0]  #TODO actually use as constant
STATION_ID_2 = PROFILE_2[0]

QUAY_1 = PROFILE_1[1]  # 17
QUAY_2 = PROFILE_2[1]   # 31

# Transit lines to display
LINE_1 = PROFILE_1[2]
LINE_2 = PROFILE_2[2]

# Line display linenames
NAME_1 = PROFILE_1[3]
NAME_2 = PROFILE_2[3]

if LCD_ON:
    from lcdbackpack import LcdBackpack
    lcdscreen = LcdBackpack('/dev/ttyACM0', 115200)
    lcdscreen.connect()
    lcdscreen.clear()
    lcdscreen.write("tramtimer v.03")


"""
Query maker for the Entur GraphQL interface (only modifying NSR StopID here)
"""
def query_maker(profile):
    query_output = """
    {{
      stopPlace(id: "{stop_id}") {{
        id
        name
        estimatedCalls(timeRange: 72100, numberOfDepartures: 20) {{
          realtime
          aimedArrivalTime
          aimedDepartureTime
          expectedArrivalTime
          expectedDepartureTime
          actualArrivalTime
          actualDepartureTime
          date
          forBoarding
          forAlighting
          destinationDisplay {{
            frontText
          }}
          quay {{
            id
          }}
          serviceJourney {{
            journeyPattern {{
              line {{
                id
                name
                transportMode
              }}
              directionType
            }}
          }}
        }}
      }}
    }}
    """.format(stop_id=profile[0])
    return query_output

def fetch_query(query):
    request = requests.post(api_url, json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed, received code: {}. {}".format(request.status_code, query))


def timeGrabber():
    """Collect departure times for given Entur quays.
    Takes two NSR quay numbers as strings as well as
    transitline ID (in format 'RUT:Line:31')
    """
    grabbedDict = defaultdict(list) # creates empty dict keyed to line number ('17' or '31')
    results = fetch_query(query_maker(PROFILE_1)) # Collect first query's results
    all_departures = results['data']['stopPlace']['estimatedCalls']

    results = fetch_query(query_maker(PROFILE_2)) # Collect second query's results
    all_departures.extend(results['data']['stopPlace']['estimatedCalls'])

    i = 0
    for headway in all_departures:
        print(QUAY_1)
        print(QUAY_2)
        if ((headway['quay']['id'] == QUAY_1) or (headway['quay']['id'] == QUAY_2)):
            # if (headway['realtime'] == True):
            print(headway)
            print(headway['quay']['id'])
            grabbedDict[headway['serviceJourney']['journeyPattern']['line']['id']].append(
                parse(headway['expectedArrivalTime']))
    return grabbedDict

def dataDebug(extract):
    print("URLDATA LENGTH " + str(len(extract)))
    print("Headways dict entries for")
    print("17:")
    print(extract[LINE_1])
    print("31:")
    print(extract[LINE_2])

def mainloop():
    # Set current time
    current = datetime.now(timezone.utc)

    # Assign trains to track for each line
    try:
        headways = timeGrabber()
    except ConnectionResetError as e:
        print("CAUGHT ConnectionResetError")
        if LCD_ON:
            lcdscreen.clear()
            lcdscreen.write("ConnResetError")
        time.sleep(10)
    except ValueError as e:
        print("VALUE ERROR:", e)
        if LCD_ON:
            lcdscreen.clear()
            lcdscreen.write("VAL Error:", e)
        time.sleep(10)
    except:
        print("ERROR CODE:", sys.exc_info()[0])
        if LCD_ON:
            lcdscreen.clear()
            lcdscreen.write("VALERROR")
        time.sleep(10)

    else:
        if DEBUG:
            dataDebug(headways)

        top = headways[LINE_1]
        bottom = headways[LINE_2]

        # Write "top" list
        if len(top) == 0:
            topcombo = NAME_1 + ":   n/a"
        if len(top) > 0:
            toptuple = dateutil.relativedelta.relativedelta(top[0], current)
            topcombo = NAME_1 + ": " + str(toptuple.minutes) + 'm '
        if len(top) > 1:
            toptuple = dateutil.relativedelta.relativedelta(top[1], current)
            topcombo += str(toptuple.minutes) + 'm '
        if len(top) > 2:
            toptuple = dateutil.relativedelta.relativedelta(top[2], current)
            topcombo += str(toptuple.minutes) + 'm'

        if DEBUG:
            print(topcombo)

        if LCD_ON:
            lcdscreen.clear()
            lcdscreen.write(topcombo)

        # Write 'bottom' list
        if len(bottom) == 0:
            bottomcombo = NAME_2 + ":   n/a"
        if len(bottom) > 0:
            bottomtuple = dateutil.relativedelta.relativedelta(
                bottom[0], current)
            bottomcombo = NAME_2 + ": " + str(bottomtuple.minutes) + 'm '
        if len(bottom) > 1:
            bottomtuple = dateutil.relativedelta.relativedelta(
                bottom[1], current)
            bottomcombo += str(bottomtuple.minutes) + 'm '
        if len(bottom) > 2:
            bottomtuple = dateutil.relativedelta.relativedelta(
                bottom[2], current)
            bottomcombo += str(bottomtuple.minutes) + 'm'

        if DEBUG:
            print(bottomcombo)

        if LCD_ON:
            lcdscreen.set_cursor_position(1, 2)
            lcdscreen.write(bottomcombo)

        time.sleep(20)


while True:
    mainloop()
