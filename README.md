# minitransportsign
Micro 'player' for a 16x2 transit arrival times sign

This project requires:
- lcdbackpack (from pypi repo) for simplified 16x2 char display comms over the
adafruit USB/i2c backpack

This project consists of two files: 

- an init script that is meant to be an at-boot toggle for the python code
- the departure-grabbing software (most of which is serial-formatting cruft) 

Together these are deployed on an RPi connected to a character display (in this case 16x2) to display the next two real time Oslo bus or tram departures. It updates itself every fifteen seconds.

NOTE: Relies on the community-made lcdbackpack library, an easier-to-use library of functions for the i2c/usb adafruit backpack.

Installation: 

1. Download minitransportsign
2. Install dependencies (listed in requirements.txt)
3. Configure a 16x2 character display via Serial/i2c/USB to a Raspberry Pi
4. Select station ID to point to
5. Run on RPI at boot with an entry at `/etc/rc.local`: 
```
python3 /home/pi/code/minitransportsign/signageFunction.py &
```

TODO:
- [ ] migration to entur API
- [ ] Further abstraction for selected lines and directions
- [X] Upgrade to python3
