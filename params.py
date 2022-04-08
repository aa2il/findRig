#! /usr/bin/python3 -u
################################################################################
#
# Params.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Command line param parser for pyKeyer.
#
################################################################################
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
################################################################################

import argparse
from rig_io.ft_tables import CONNECTIONS,RIGS

################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()

        # Unflagged arg allowing us to check for a specific rig being connected
        # There is overlap with the legacy -rig flag which we should
        # unwind at some point
        arg_proc.add_argument('Rigs', metavar='Rigs',
                              type=str, nargs='*', default=None,
                              help='Rig to check for')

        arg_proc.add_argument("-rig", help="Connection Type",
                              type=str,default=None,nargs='+',
                              choices=CONNECTIONS+['NONE']+RIGS)
        arg_proc.add_argument("-port", help="Connection Port",
                              type=int,default=0)
        arg_proc.add_argument("-m", help="Get rig mode",
                              action='store_true')
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
        arg_proc.add_argument("-PAMP", help="Set Pre-amp",
                              type=int,default=None)
        arg_proc.add_argument("-ATTEN", help="Set Attenuator",
                              type=int,default=None)
        arg_proc.add_argument("-A2B", help="Copy VFO A to VFO B",
                              action='store_true')
        arg_proc.add_argument("-w", help="Rig command",
                              type=str,default=None)
        arg_proc.add_argument("-verbosity", help="VERBOSITY",
                              type=int,default=0)
        args = arg_proc.parse_args()

        self.PORT      = args.port

        if len(args.Rigs)>0:
            self.connection = None
            self.rig  = args.Rigs[0]
            self.PORT = self.rig
        elif args.rig:
            self.connection    = args.rig[0]
            if len(args.rig)>=2:
                self.rig       = args.rig[1]
            else:
                self.rig       = None
        else:
            self.connection = None
            self.rig        = None
    
        self.GET_MODE  = args.m
        self.SET_MODE  = args.M
        self.SET_FILT  = args.FILT
        self.RUN_CMD   = args.w
        self.SET_PWR   = args.PWR
        self.SET_MON   = args.MON
        self.SET_TUNER = args.TUNER
        self.SET_FRONT_END = args.PAMP!=None or args.ATTEN!=None
        self.COPY_A2B  = args.A2B
        self.PAMP      = args.PAMP
        self.ATTEN     = args.ATTEN

        #print('Hey:',args.m,GET_MODE)
        #print('Hey:',args.PAMP,args.ATTEN,SET_FRONT_END)

        self.VERBOSITY = args.verbosity

        self.sock = None
