#!/usr/bin/env -S uv run --script
#
#! /home/joea/miniconda3/envs/aa2il/bin/python -u
#
# NEW: /home/joea/miniconda3/envs/aa2il/bin/python -u
# OLD: /usr/bin/python3 -u 
############################################################################
#
# Find Rig - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
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
from rig_io import try_port
from rig_io import socket_io
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

    if P.VERBOSITY>0:
        print('P.rig=',P.rig)
        print('rig_type =',P.sock.rig_type)
        print('rig_type1=',P.sock.rig_type1)
        print('rig_type2=',P.sock.rig_type2)
        #sys.exit(0)
    
elif True:

    if P.VERBOSITY>0:
        print('P.rig=',P.rig)
    
    # This works on windoz & linux - New pathway
    for rig_name in P.rig:
        if rig_name[0:2]=='IC':
            ICOM=rig_name
        else:
            ICOM=None
        port,vid_pid=find_serial_device(rig_name,0,VERBOSITY=P.VERBOSITY)
        for baud in [38400]:

            # Try to illicit a response from a rig on this port
            rig=try_port(port,baud,P.VERBOSITY,ICOM=ICOM)
            if P.VERBOSITY>0:
                print('FIND RIG: rig_name=',rig_name,'\tport=',port,'\trig=',rig)

            if rig:

                # Found it - print out rig type, do any inits and exit
                if P.VERBOSITY>0:
                    print('rig=',rig)
                    #print('rig0=',rig[0])
                    #print('rig1=',rig[1])
                    #print('rig2=',rig[2])
                    
                P.sock = rig[2]
                if rig[1]=='IC9700' or rig[1]=='IC7300':
                    # Set time - why ????!!!!
                    #sock.set_date_time()
                    pass
                elif rig[1]=='FTdx3000':
                    # Make sure full-power and ant tuner is on
                    try:
                        P.sock.set_power(99)
                        P.sock.tuner(1)
                        #P.sock.get_response('BY;EX177100;')         # Make sure max TX is also set - Old style b4 4.6.2
                        P.sock.get_response('W EX177100; 0')         # Make sure max TX is also set
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
                if rig[1]=='IC9700' or rig[1]=='IC7300':
                    # Set time - why ????!!!!
                    #sock.set_date_time()
                    pass
                elif rig[1]=='FTdx3000':
                    # Make sure full-power and ant tuner is on
                    P.sock.set_power(99)
                    P.sock.tuner(1)
                    #P.sock.get_response('BY;EX177100;')         # Make sure max TX is also set  - Old style b4 4.6.2
                    P.sock.get_response('W EX177100; 0')         # Make sure max TX is also set
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
if P.sock and False:
    if P.sock.rig_type=='FLRIG':
        if P.sock.rig_type2=='UNKNOWN':
            P.sock.rig_type2=rig
            
if P.VERBOSITY>0:
    print('\nRig inits ...')
    print('rig=',rig)
    if P.sock:
        print('rig_type =',P.sock.rig_type)
        print('rig_type1=',P.sock.rig_type1)
        print('rig_type2=',P.sock.rig_type2)
    
if P.GET_MODE:
    if P.VERBOSITY>0:
        print('FIND RIG: Getting mode ...')
    mode=P.sock.get_mode()
    print('mode=',mode)

if P.SET_MODE!=None:
    if P.VERBOSITY>0:
        print('FIND RIG: Setting mode ...')
    P.sock.set_mode(P.SET_MODE)
    
if P.SET_FILT!=None:
    if P.VERBOSITY>0:
        print('FIND RIG: Setting filter ...')
    P.sock.set_filter(P.SET_FILT,P.SET_MODE)
    
if P.SET_PWR!=None:
    if P.VERBOSITY>0:
        print('FIND RIG: SETTING POWER=',P.SET_PWR)
    P.sock.set_power(P.SET_PWR)
    
if P.SET_MON!=None:
    if P.VERBOSITY>0:
        print('FIND RIG: SETTTNG MONITOR=',P.SET_MON)
    P.sock.set_monitor_gain(P.SET_MON)
    
if P.SET_ANT!=None:
    if P.VERBOSITY>0:
        print('FIND RIG: SETTTNG ANTENNA=',P.SET_ANT)
    P.sock.set_ant(P.SET_ANT)
    
if P.SET_IFSHIFT!=None:
    if P.VERBOSITY>0:
        print('FIND RIG: SETTTNG IFSHIFT=',P.SET_IFSHIFT)
    P.sock.set_if_shift(P.SET_IFSHIFT)
    
if P.sock and P.SET_BREAK!=None:
    if P.VERBOSITY>0:
        print('FIND RIG: SETTING BREAK-IN=',P.SET_BREAK)
    P.sock.set_breakin(P.SET_BREAK)
    
if P.SET_TUNER!=None:
    if P.VERBOSITY>0:
        print('FIND RIG: SETTING TUNER=',P.SET_TUNER)
    P.sock.tuner(P.SET_TUNER)
    
if P.SET_FRONT_END:
    if P.VERBOSITY>0:
        print('FIND RIG: SETTING FRONT END=',P.AMP,P.ATTEN)
    P.sock.frontend(1,P.PAMP,P.ATTEN)

if P.COPY_A2B:
    if P.VERBOSITY>0:
        print('FIND RIG: COPY a to B ...')
    #P.sock.get_response('BY;AB;')                # Old style b4 4.6.2
    P.sock.get_response('W AB; 0') 
    #sock.set_vfo(op='A->B')
    
if P.RUN_CMD!=None:
    if rig in ["FTdx3000","FT991a"]:
        P.RUN_CMD=P.RUN_CMD.replace("'","")+';'
    if P.VERBOSITY>0 or True:
        print('FIND RIG: Running command=',P.RUN_CMD)
    if P.sock:
        reply=P.sock.get_response(P.RUN_CMD)
    else:
        reply=None
    print(reply)
    
    
