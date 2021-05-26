#! /usr/bin/python3

# Find Rig - J.B.Attili - 2019

# Script to determine rig type attached to a serial port.

############################################################################

import sys
from os import listdir
from rig_io.direct_io import *

############################################################################

# User params
PATH='/dev/serial/by-id'
VERBOSITY=0

############################################################################

if VERBOSITY>0:
    print("Hello World!")

#onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
#sock = socket_io.open_rig_connection('DIRECT',0,0,0,'findRig')

# Get list of USB ports
try:
    files = listdir(PATH)
except:
    files=[]

#print('Files=',files)    

# Sift through list of usb ports
for f in files:
    port=PATH+'/'+f
    if VERBOSITY>0:
        print('\n'+port)

    # The modern rigs have been set to operate at 38400 but the old
    # TS850 can only go up to 4800 bps
    for baud in [38400,4800]:

        # Try to illicit a response from a rig on this port
        rig=try_port(port,baud,VERBOSITY)
        if rig:

            # Found it - print out rig type and exit
            print(rig[1])
            if rig[1]=='IC9700' and True:
                # Set time
                #sock = direct_connect(0,0)
                sock = rig[2]
                sock.set_date_time()
            elif rig[1]=='FT991a' and True:
                # Turn off split mode - this rig seems to get into split quite a bit
                #print('Hey')
                sock = rig[2]
                sock.split_mode(0)
                
            sys.exit(0)
            
