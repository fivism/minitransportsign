# minitransportsign
An exploration of framework for driving home transportation headways signs.

This project consists of two files: 

- an init script that is meant to be an at-boot toggle for the python code
- the departure-grabbing software (most of which is serial-formatting cruft) 

Together these are deployed on an RPi connected to a character display (in this case 16x2) to display the next two real time Oslo bus or tram departures. It updates itself every fifteen seconds.
