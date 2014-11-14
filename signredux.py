## This seeks out the bicycle counts for 49 (Frognerveien) and 55 (Bygdoy) 
## from the most recent scrape in /scrapes
##
##
## Ideally in the future it will query a db where the scrapes are collected
##
import serial
import json, os, glob, sys, urllib2
import time, datetime, dateutil.relativedelta
from time import sleep


def print(s, **kwargs):
    __builtins__.print(time.strftime("[%b %d %H:%M:%S] ") + s, **kwargs)

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

def get_caltrain(direction):
    try:
        #Use the below URL to get stop IDs
        #http://services.my511.org/Transit2.0/GetStopsForRoutes.aspx?token=c1426e9c-b9d7-4dc5-a561-84a78e1f0b86&routeIDF=Caltrain~LOCAL~SB2
        
        stopdirs = {"70242":"South","70241":"North"}
        url = "http://services.my511.org/Transit2.0/GetNextDeparturesByStopCode.aspx"
        output = ["Caltrain %s" % direction]

        for stopcode in stopdirs.keys():
            if stopdirs[stopcode] == direction:
                query = urllib.parse.urlencode({"token":"abcd123", "stopcode":"%s" % stopcode})
                dom = xml.dom.minidom.parse(urllib.request.urlopen("%s?%s" % (url,query)))
                routes = dom.getElementsByTagName("Route")
                depart_times = []
                for route in routes:

                    
                    for depart_time in route.getElementsByTagName('DepartureTime'):
                        depart_times.append(depart_time.childNodes[0].nodeValue)
                if depart_times != []:
                    depart_times.sort()
                    output.append("In %s minutes" % ",".join(depart_times[0:2]))

        return output
    except SerialException as e: raise
    except:
        print (traceback.format_exc())


#LCD Command definitions
CLS = b'\xFE\x58'           #this will clear the screen of any text
HOME = b'\xFE\x48'          #place the cursor at location (1, 1)
CURSOR_POS = b'\xFE\x47'    #set the position of text entry cursor. Column and row numbering starts with 1 so the first position in the very top left is (1, 1)
CURSOR_BACK = b'\xFE\x4C'   #move cursor back one space, if at location (1,1) it will 'wrap' to the last position.
CURSOR_FWD = b'\xFE\x4D'    #move cursor forward one space, if at the last location location it will 'wrap' to the (1,1) position.

CURSOR_UNDERLINE_ON = b'\xFE\x4A'   #turn on the underline cursor
CURSOR_UNDERLINE_OFF = b'\xFE\x4B'  #turn off the underline cursor
CURSOR_BLINK_ON = b'\xFE\x53'       #turn on the blinking block cursor
CURSOR_BLINK_OFF = b'\xFE\x54'      #turn off the blinking block cursor

BACKLIGHT_ON=b'\xFE\x42'    #This command turns the display backlight on
BACKLIGHT_OFF=b'\xFE\x46'   #turn the display backlight off

CONTRAST = b'\xFE\x50'      #Set the display contrast. Add a byte value to this constant.
                            #In general, around 180-220 value is what works well.
                            #Setting is saved to EEPROM

BACKLIGHT_BRIGHTNESS = b'\xFE\x99'          #set the overall brightness of the backlight (the color component is set separately - brightness setting takes effect after the color is set)
BACKLIGHT_COLOR = b'\xFE\xD0'               #Sets the backlight to the red, green and blue component colors. The values of can range from 0 to 255 (one byte), last 3 bytes. This is saved to EEPROM
BACKLIGHT_ORANGE= b'\xFE\xD0\xFF\x01\x00'   #Sample orange color for the backlight
BACKLIGHT_TEAL= b'\xFE\xD0\x00\xFF\xFF'     #Sample teal color
BACKLIGHT_RED= b'\xFE\xD0\xFF\x00\x00'
BACKLIGHT_GREEN= b'\xFE\xD0\x00\xFF\x00'
AUTOSCROLL_ON = b'\xFE\x51'                 #this will make it so when text is received and there's no more space on the display
                                            #the text will automatically 'scroll' so the second line becomes the first line, etc.
                                            #new text is always at the bottom of the display
RGB_RED = (255,0,0)
RGB_GREEN = (0,255,0)
RGB_BLUE = (0,0,255)
RGB_TEAL = (0,255,255)
RGB_ORANGE=(255,1,0)
RGB_PURPLE=(255,0,255)
RGB_BABYBLUE = (240, 240, 255)
RGB_AVOCADO = (86,130,3)

AUTOSCROLL_OFF = b'\xFE\x52'                #this will make it so when text is received and there's no more space on the display, the text will wrap around to start at the top of the display.
#END LCD Command Definitions

def set_lcd_color(ser,r,g,b):
    try:
        ser.cur_color = {"R":r,"G":g,"B":b}
        ser.write(BACKLIGHT_COLOR+bytes([r,g,b]))
    except SerialException as e: raise
    except:
        print (traceback.format_exc())

def init_lcd(ser):
    try:
        ser.cur_color = {"R":0,"G":0,"B":0}
        
        ser.write(CONTRAST + bytes([227])) #185 seems to be a good value for contrast
        ser.write(BACKLIGHT_BRIGHTNESS + bytes([255]))        
        #ser.write(BACKLIGHT_TEAL)      # Go SHARKS
        
        ser.write(AUTOSCROLL_OFF)
        ser.write(CLS) #clear display
        
        set_lcd_color(ser,128,128,128)
    except SerialException as e: raise
    except:
        print (traceback.format_exc())

def mainloop():
    sys.stdout = simpleLogger("lcd.log")
    sys.stderr = simpleLogger("lcd-err.log")
    try:
        ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600)  # open first serial port
    except:
        ser = serial.Serial(port='/dev/ttyACM1', baudrate=9600)  # try the second

    init_lcd(ser)


    while(1):
        scroll_text(ser,0.35,5,RGB_GREEN,*get_caltrain("North"))
        scroll_text(ser,0.35,5,RGB_AVOCADO,*get_caltrain("South"))
        scroll_text(ser,0.35,5,RGB_ORANGE,*get_bus_times())

        timedelta = time.mktime(time.strptime("11/23/2014 9:00AM", "%m/%d/%Y %I:%M%p"))-time.time()

        days = int(timedelta/(3600*24))
        hrs = int((timedelta - int(timedelta/(3600*24))*3600*24)/3600)
        min = int((timedelta - int(timedelta/3600)*3600)/60)

        scroll_text(ser,0.35,5,RGB_BABYBLUE,"Time 'til Hawaii", "%sd %shrs %smin" % (days, hrs, min))
        scroll_text(ser,0.35,5,RGB_ORANGE,*get_bus_times())
        scroll_text(ser,0.35,5,RGB_PURPLE,*get_weather())
        scroll_text(ser,0.35,5,RGB_ORANGE,*get_bus_times())
        #scroll_text(ser,0.38,1,RGB_RED,*get_quake_data())

        
        get_nhl_live_games(ser,speed=3)             #NHL sets its own color
    
while(1):
    try:      
        mainloop()
    except:
        print (traceback.format_exc())
        time.sleep(5)



##### OLD #######
##### OLD #######
##### OLD #######


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


