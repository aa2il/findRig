#! /usr/bin/python3
############################################################################
#
# Find Rig - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
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
from rig_io.direct_io import try_port
import rig_io.socket_io as socket_io
from params import *
from pprint import pprint
import serial.tools.list_ports
from utilities import find_serial_device

############################################################################

# User params
DEV_PATH='/dev/serial/by-id'

############################################################################

P=PARAMS()
rig=None

if P.VERBOSITY>0:
    print("\n\n***********************************************************************************")
    print("\nStarting findRig  ...")
    print("P=")
    pprint(vars(P))

# If a rig & connection have been specified, connect to it, presumably to
# send it some commands
if P.connection:

    if P.VERBOSITY>0:
        print('\nOpening',P.connection,' connection to rig',
              P.rig,' on port',P.PORT,'...')
    P.sock = socket_io.open_rig_connection(P.connection,0,P.PORT,0,
                                           'PROBE',rig=P.rig)
    
    if not P.sock.active:
        print('*** No connection available to rig ***')
        sys.exit(0)
    rig=P.rig

elif True:

    if P.VERBOSITY>0:
        print('P.rig=',P.rig)
    
    # This works on windoz & linux - New pathway
    for rig_name in P.rig:
        if rig_name[0:2]=='IC':
            ICOM=True
        else:
            ICOM=False
        port=find_serial_device(rig_name,0,VERBOSITY=P.VERBOSITY)
        for baud in [38400]:

            # Try to illicit a response from a rig on this port
            rig=try_port(port,baud,P.VERBOSITY,ICOM=ICOM)
            if P.VERBOSITY>0:
                print('rig_name=',rig_name,'\tport=',port,'\trig=',rig)

            if rig:

                # Found it - print out rig type, do any inits and exit
                if P.VERBOSITY>0:
                    print('rig=',rig)
                    #print('rig0=',rig[0])
                    #print('rig1=',rig[1])
                    #print('rig2=',rig[2])
                    
                P.sock = rig[2]
                if rig[1]=='IC9700':
                    # Set time - why ????!!!!
                    #sock.set_date_time()
                    pass
                elif rig[1]=='FTdx3000':
                    # Make sure full-power and ant tuner is on
                    try:
                        P.sock.set_power(99)
                        P.sock.tuner(1)
                        P.sock.get_response('BY;EX177100;')         # Make sure max TX is also set
                    except:
                        break
                elif rig[1]=='FT991a':
                    # Turn off split mode - this rig seems to get into split quite a bit
                    #print('Hey')
                    P.sock.split_mode(0)
                
                #sys.exit(0)
                rig=rig[1]
                break
        else:
            continue         # Iterate outer loop if we didn't break
        break                # Quit outer loop if we did break

else:          
    
    # Old pathway
    # No conenction specified - get list of USB ports
    try:
        files = listdir(DEV_PATH)
    except:
        files=[]

    if P.VERBOSITY>0:
        print('rig=',P.rig)
        print('\nUSB ports found:')
        for f in files:
            print(f)    

    # Sift through list of usb ports
    for f in files:
        port=DEV_PATH+'/'+f
        if P.VERBOSITY>0:
            print('\n------------------------------------------------')
            print('Trying port',port,'...')

        # Skip over the obvious
        if 'GPS' in f or 'arduino' in f:
            if P.VERBOSITY>0:
                print('... skipping this one')
            continue

        # The modern rigs have been set to operate at 38400 but my 
        # old TS850 can only go up to 4800 bps
        #for baud in [38400,4800]:
        for baud in [38400]:

            # Try to illicit a response from a rig on this port
            rig=try_port(port,baud,P.VERBOSITY)
            if rig:

                # Found it - print out rig type, do any inits and exit
                if P.VERBOSITY>0:
                    print('rig=',rig)
                    #print('rig0=',rig[0])
                    #print('rig1=',rig[1])
                    #print('rig2=',rig[2])
                    
                P.sock = rig[2]
                if rig[1]=='IC9700':
                    # Set time - why ????!!!!
                    #sock.set_date_time()
                    pass
                elif rig[1]=='FTdx3000':
                    # Make sure full-power and ant tuner is on
                    P.sock.set_power(99)
                    P.sock.tuner(1)
                    P.sock.get_response('BY;EX177100;')         # Make sure max TX is also set
                elif rig[1]=='FT991a':
                    # Turn off split mode - this rig seems to get into split quite a bit
                    #print('Hey')
                    P.sock.split_mode(0)
                
                #sys.exit(0)
                rig=rig[1]
                break
        else:
            continue         # Iterate outer loop if we didn't break
        break                # Quit outer loop if we did break

# Print final result or None if nothing found
if type(rig)==list:
    rig=rig[1]
print(rig)

# Do any inits
if P.sock:
    if P.sock.rig_type=='FLRIG':
        if P.sock.rig_type2=='UNKNOWN':
            P.sock.rig_type2=rig
            
if P.VERBOSITY>0:
    print('\nRig inits ...')
    print('rig=',rig)
    if P.sock:
        print('rig_type1=',P.sock.rig_type1)
        print('rig_type2=',P.sock.rig_type2)
    
if P.GET_MODE:
    mode=P.sock.get_mode()
    print('mode=',mode)

if P.SET_MODE!=None:
    P.sock.set_mode(P.SET_MODE)
    
if P.SET_FILT!=None:
    P.sock.set_filter(P.SET_FILT,P.SET_MODE)
    
if P.SET_PWR!=None:
    P.sock.set_power(P.SET_PWR)
    
if P.SET_MON!=None:
    #print('SET_MON=',P.SET_MON)
    P.sock.set_monitor_gain(P.SET_MON)
    
if P.sock and P.SET_BREAK!=None:
    #print('rig=',rig)
    #print('SET_BREAK=',P.SET_BREAK)
    cmd='BY;BI'+str(P.SET_BREAK)+';'
    P.sock.get_response(cmd)
    
if P.SET_TUNER!=None:
    P.sock.tuner(P.SET_TUNER)
    
if P.SET_FRONT_END:
    P.sock.frontend(1,P.PAMP,P.ATTEN)

if P.COPY_A2B:
    P.sock.get_response('BY;AB;')
    #sock.set_vfo(op='A->B')
    
if P.RUN_CMD!=None:
    #print('rig=',rig)
    if rig in ["FTdx3000","FT991a"]:
        P.RUN_CMD=P.RUN_CMD.replace("'","")+';'
    #print('cmd=',P.RUN_CMD)
    if P.sock:
        reply=P.sock.get_response(P.RUN_CMD)
    else:
        reply=None
    print(reply)
    
    
