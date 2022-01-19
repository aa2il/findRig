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
import rig_io.socket_io as socket_io

############################################################################

# User params
PATH='/dev/serial/by-id'

############################################################################

if VERBOSITY>0:
    print("Hello World!")

arg_proc = argparse.ArgumentParser()
arg_proc.add_argument("-rig", help="Connection Type",
                      type=str,default=None,nargs='+',
                      choices=CONNECTIONS+['NONE']+RIGS)
arg_proc.add_argument("-port", help="Connection Port",
                      type=int,default=0)
arg_proc.add_argument("-m", help="Get rig mode",action='store_true')
arg_proc.add_argument("-M", help="Set rig mode",
                      type=str,default=None,
                      choices=['CW','SSB','RTTY'])
arg_proc.add_argument("-FILT", help="Set rig filter",
                      type=str,default=None,
                      choices=['Narrow','Wide'])
arg_proc.add_argument("-PWR", help="Rig Power",
                      type=int,default=None)
arg_proc.add_argument("-MON", help="Monitor Level",
                      type=int,default=None)
arg_proc.add_argument("-TUNER", help="Tuner On/Off",
                      type=int,default=None)
arg_proc.add_argument("-w", help="Rig command",
                      type=str,default=None)
arg_proc.add_argument("-verbosity", help="VERBOSITY",
                      type=int,default=0)
args = arg_proc.parse_args()

if not args.rig:
    connection = None
    rig        = None
else:
    connection    = args.rig[0]
    if len(args.rig)>=2:
        rig       = args.rig[1]
    else:
        rig       = None
PORT      = args.port

GET_MODE  = args.m
SET_MODE  = args.M
SET_FILT  = args.FILT
RUN_CMD   = args.w
SET_PWR   = args.PWR
SET_MON   = args.MON
SET_TUNER = args.TUNER

VERBOSITY = args.verbosity

############################################################################

if VERBOSITY>0:
    print("\n\n***********************************************************************************")
    print("\nStarting findRig  ...")
    print('connection=',connection)

# If a rig has been specified, connect to it
if connection:
    
    sock = socket_io.open_rig_connection(connection,0,PORT,0,'PROBE',rig=rig)
    if not sock.active:
        print('*** No connection available to rig ***')
        sys.exit(0)

else:
    
    # No conenction specified - get list of USB ports
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
                if VERBOSITY>0:
                    print('rig=',rig)
                    #print('rig0=',rig[0])
                    #print('rig1=',rig[1])
                    #print('rig2=',rig[2])
                    
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
                
            #sys.exit(0)
            break


# Do any inits
if VERBOSITY>0:
    print('\nRig inits ...')
    print(rig)
    print(sock.rig_type1)
    print(sock.rig_type2)
    
if GET_MODE!=None:
    mode=sock.get_mode()
    print(mode)

if SET_MODE!=None:
    sock.set_mode(SET_MODE)
    
if SET_FILT!=None:
    sock.set_filter(SET_FILT)
    
if SET_PWR!=None:
    sock.set_power(SET_PWR)
    
if SET_MON!=None:
    sock.set_monitor_gain(SET_MON)
    
if SET_TUNER!=None:
    sock.tuner(SET_TUNER)
    
if RUN_CMD!=None:
    if rig in ["FTdx3000","FT991a"]:
        RUN_CMD=RUN_CMD.replace("'","")+';'
    print('cmd=',RUN_CMD)
    reply=sock.get_response(RUN_CMD)
    print('reply=',reply)
    
    
