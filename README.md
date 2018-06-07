# minitransportsign
Micro 'player' for a 16x2 transit arrival times sign

This project requires:
- lcdbackpack (from pypi repo) for simplified 16x2 char display comms over the
adafruit USB/i2c backpack

This project consists of two files: 

- an init script that is meant to be an at-boot toggle for the python code
- the departure-grabbing software (most of which is serial-formatting cruft) 

Together these are deployed on an RPi connected to a character display (in this case 16x2) to display the next two real time Oslo bus or tram departures. It updates itself every fifteen seconds.
