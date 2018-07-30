#!/usr/bin/python3
##
# Two line sign that shows two departures for two lines simultaneously
# and outputs specifically to a 16x2 character display.

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

# Specify quay IDs for each
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
        estimatedCalls(timeRange: 72100, numberOfDepartures: 30) {{
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

    for headway in all_departures:
        if ((headway['quay']['id'] == QUAY_1) or (headway['quay']['id'] == QUAY_2)):
            grabbedDict[headway['serviceJourney']['journeyPattern']['line']['id']].append(
                parse(headway['expectedArrivalTime']))
    return grabbedDict

def dataDebug(extract):
    print("URLDATA LENGTH " + str(len(extract)))
    print("Headways dict entries for")
    print(NAME_1 + ": ")
    print(extract[LINE_1])
    print(NAME_2 + ": ")
    print(extract[LINE_2])

def line_maker(hdways, line_name):
    # Set current time
    current = datetime.now(timezone.utc)
    minute_list = []

    for headway in hdways:
        diff = dateutil.relativedelta.relativedelta(headway, current)
        mins = diff.minutes
        if diff.hours > 0:
            mins += diff.hours * 60
        minute_list.append(str(mins) + "m")
        if len(minute_list) == 3:
            break

    # Time display conditionals
    if len(hdways) == 0:
        out_string = line_name + ":   n/a"
    if len(hdways) > 0:
        out_string = line_name + ": " + ' '.join(minute_list)

    return out_string

def mainloop():
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

        tops = headways[LINE_1]
        bottoms = headways[LINE_2]

        top_line = line_maker(NAME_1, tops)        # Write top list
        if DEBUG:
            print(top_line)
        if LCD_ON:
            lcdscreen.clear()
            lcdscreen.write(top_line)

        bottom_line = line_maker(NAME_2, bottoms)  # Write bottom list
        if DEBUG:
            print(bottom_line)
        if LCD_ON:
            lcdscreen.set_cursor_position(1, 2)
            lcdscreen.write(bottom_line)

        time.sleep(20)

while True:
    mainloop()
