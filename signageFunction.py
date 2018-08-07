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

LCD_ON = False  # for testing with/without serial LCD connection
DEBUG = True  # set extra output on
PROFILE_FILE = "profiles.txt" # config file with ET_CLIENT_NAME and stations

def prof_reader(filename):
    """
    Returns chosen et_client_name (for Entur API)
    and station profiles from profiles file
    """
    new_dict = dict()
    client_name = ""
    with open(filename) as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        client_name = lines[0]
        lines = lines[1:]
        for line in lines:
            line = line.split()
            new_dict[line[0]] = line[1:5]
    return client_name, new_dict

try:
    et_client_name, ST_DICT = prof_reader(PROFILE_FILE)
except FileNotFoundError:
    print("profiles.txt missing! Create a profiles file with following format:")
    print("\tet-client-name")
    print("\tprofile-name1 NSR-Registry-ID NSR-Quay-ID LineID display-name")
    print("\tprofile-name2 \" \" \" \"")
    sys.exit()

headers = {'ET-Client-Name': et_client_name}
api_url = 'https://api.entur.org/journeyplanner/2.0/index/graphql'

# Selected profiles to display (Only 2 profiles on 16x2 display)
PROFILE_1 = ST_DICT['21-west']
PROFILE_2 = ST_DICT['31-downtown']

# Station and quays to seek
STATION_ID = PROFILE_1[0]
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
    stop_id = profile[0]
    query_output = """
    {{
      stopPlace(id: "{0}") {{
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
    """.format(stop_id)
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
        if len(minute_list) == 3:   # never care about more than 3
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

        top_line = line_maker(tops, NAME_1)        # Write top list
        if DEBUG:
            print(top_line)
        if LCD_ON:
            lcdscreen.clear()
            lcdscreen.write(top_line)

        bottom_line = line_maker(bottoms, NAME_2)  # Write bottom list
        if DEBUG:
            print(bottom_line)
        if LCD_ON:
            lcdscreen.set_cursor_position(1, 2)
            lcdscreen.write(bottom_line)

        time.sleep(20)

while True:
    mainloop()
