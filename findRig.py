#! /usr/bin/python3
############################################################################
#
# Find Rig - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Script to determine rig type attached to a serial port and do any common
# inits.
#
############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################

import sys
from os import listdir
from rig_io.direct_io import *
import argparse

############################################################################

# User params
PATH='/dev/serial/by-id'
#VERBOSITY=0

############################################################################

if VERBOSITY>0:
    print("Hello World!")

arg_proc = argparse.ArgumentParser()
arg_proc.add_argument("-verbosity", help="VERBOSITY",
                              type=int,default=0)
args = arg_proc.parse_args()
VERBOSITY=args.verbosity

# Get list of USB ports
try:
    files = listdir(PATH)
except:
    files=[]

if VERBOSITY>0:
    print('\nUSB ports found:')
    for f in files:
        print(f)    

# Sift through list of usb ports
for f in files:
    port=PATH+'/'+f
    if VERBOSITY>0:
        print('\n------------------------------------------------')
        print('Trying port',port,'...')

    # Skip over the obvious
    if 'GPS' in f or 'arduino' in f:
        if VERBOSITY>0:
            print('... skipping this one')
        continue

    # The modern rigs have been set to operate at 38400 but my 
    # old TS850 can only go up to 4800 bps
    #for baud in [38400,4800]:
    for baud in [38400]:

        # Try to illicit a response from a rig on this port
        rig=try_port(port,baud,VERBOSITY)
        if rig:

            # Found it - print out rig type, do any inits and exit
            print(rig[1])
            sock = rig[2]
            if rig[1]=='IC9700':
                # Set time - why ????!!!!
                #sock.set_date_time()
                pass
            elif rig[1]=='FTdx3000':
                # Make sure full-power and ant tuner is on
                sock.set_power(99)
                sock.tuner(1)
                sock.get_response('BY;EX177100;')         # Make sure max TX is also set
            elif rig[1]=='FT991a':
                # Turn off split mode - this rig seems to get into split quite a bit
                #print('Hey')
                sock.split_mode(0)
                
            sys.exit(0)
            
