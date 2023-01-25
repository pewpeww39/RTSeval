# -*- coding: utf-8 -*-

## DO NOT CHANGE ABOVE LINE

# Python for Test and Measurement
#
# Requires VISA installed on Control PC
# 'keysight.com/find/iosuite'
# Requires PyVISA to use VISA in Python
# 'http://pyvisa.sourceforge.net/pyvisa/'

## Keysight IO Libraries 17.1.19xxx
## Anaconda Python 2.7.7 32 bit
## pyvisa 1.6.3
## Windows 7 Enterprise, 64 bit

##"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
## Copyright © 2015 Keysight Technologies Inc. All rights reserved.
##
## You have a royalty-free right to use, modify, reproduce and distribute this
## example files (and/or any modified version) in any way you find useful, provided
## that you agree that Keysight has no warranty, obligations or liability for any
## Sample Application Files.
##
##"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

##############################################################################################################################################################################
##############################################################################################################################################################################
## Import Python modules
##############################################################################################################################################################################
##############################################################################################################################################################################

## import python modules - Not all of these are used in this program; provided for reference
import sys
import visa
import time
import struct
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

##############################################################################################################################################################################
##############################################################################################################################################################################
## Intro, general comments, and instructions
##############################################################################################################################################################################
##############################################################################################################################################################################

## This example program is provided as is and without support. Keysight is not responsible for modifications.

## Keysight IO Libraries 17.1.19xxx was used.
## Anaconda Python 2.7.7 32 bit is used
## pyvisa 1.6.3 is used
## Windows 7 Enterprise, 64 bit (has implications for time.clock if ported to unix type machine, use timt.time instead)

## HiSlip and Socket connections not supported

## DESCRIPTION OF FUNCTIONALITY
## This scirpt shows how to save a screenshot from an InfiniiVision scope to a PC/LAPTOP
## This script should work for all InfiniiVision and InfiniiVision-X oscilloscopes:
## DSO5000A, DSO/MSO6000A/L, DSO/MSO7000A/B, DSO/MSO-X2000A, DSO/MSO-X3000A/T, DSO/MSO-X4000A, DSO/MSO-X6000A
## NO ERROR CHECKING IS INCLUDED

## INSTRUCTIONS
## Edit in the VISA address of the oscilloscope
## Edit in the file save locations

## CAUTION: This script WILL overwrite previously saved files
## ALWAYS DO SOME TEST RUNS!!!!! and ensure you are getting what you want and it is later usable!!!!!

##############################################################################################################################################################################
##############################################################################################################################################################################
## DEFINE CONSTANTS
##############################################################################################################################################################################
##############################################################################################################################################################################

## Initialization constants
VISA_ADDRESS = "USB0::0x0957::0x17A0::MY51500437::0::INSTR" # Get this from Keysight IO Libraries Connection Expert #Note: sockets are not supported in this revision of the script, and pyVisa 1.6.3 does not support HiSlip
GLOBAL_TOUT =  10000 # IO time out in milliseconds

## Data Save constants
BASE_FILE_NAME = "my_screenshot"
BASE_DIRECTORY = "C:\\Users\\Public\\"
    ## IMPORTANT NOTE:  This script WILL overwrite previously saved files

##############################################################################################################################################################################
##############################################################################################################################################################################
## Main code
##############################################################################################################################################################################
##############################################################################################################################################################################

##############################################################################################################################################################################
##############################################################################################################################################################################
## Connect and initialize scope
##############################################################################################################################################################################
##############################################################################################################################################################################

## Define VISA Resource Manager & Install directory
## This directory will need to be changed if VISA was installed somewhere else.
rm = visa.ResourceManager('C:\\Windows\\System32\\visa32.dll') # this uses pyvisa
## This is more or less ok too: rm = visa.ResourceManager('C:\\Program Files (x86)\\IVI Foundation\\VISA\\WinNT\\agvisa\\agbin\\visa32.dll')
## In fact, it is generally not needed to call it explicitly
## rm = visa.ResourceManager()

## Open Connection
## Define & open the scope by the VISA address ; # this uses pyvisa
KsInfiniiVisionX = rm.open_resource(VISA_ADDRESS)

## Set Global Timeout
## This can be used wherever, but local timeouts are used for Arming, Triggering, and Finishing the acquisition... Thus it mostly handles IO timeouts
KsInfiniiVisionX.timeout = GLOBAL_TOUT

#clear the instrument bus
KsInfiniiVisionX.clear()

## DO NOT RESET THE SCOPE!

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define a Function for Binary Data Management
##############################################################################################################################################################################
##############################################################################################################################################################################

## Originally Written by: John Dorighi, Inside Application Engineer
## Modified, Expanded, and Improved for general use by: John-Michael O'Brien, Inside Application Engineer
## DO NOT change this.
## Python function can be defined anywhere in a script as long as they are defined BEFORE they are called.

def binblock_raw(data_in):
    # This function interprets the header for a definite binary block
    # and returns the raw binary data for both definite and indefinite binary blocks

    startpos=data_in.find("#")
    if startpos < 0:
        raise IOError("No start of block found")
    lenlen = int(data_in[startpos+1:startpos+2]) # get the data length

    # If it's a definite length binary block
    if lenlen > 0:
        # Get the length from the header
        offset = startpos+2+lenlen
        datalen = int(data_in[startpos+2:startpos+2+lenlen])
    else:
        # If it's an indefinite length binary block get the length from the transfer itself
        offset = startpos+2
        datalen = len(data_in)-offset-1

    # Extract the data out into a list.
    return data_in[offset:offset+datalen]

##############################################################################################################################################################################
##############################################################################################################################################################################
## Get and parse the IDN string to determine scope generation
##############################################################################################################################################################################
##############################################################################################################################################################################

## Get and parse IDN string
IDN = str(KsInfiniiVisionX.query("*IDN?"))
## Parse IDN
IDN = IDN.split(',') # IDN parts are separated by commas, so parse on the commas
#mfg = IDN[0] # Python indices start at 0
model = IDN[1]
#SN = IDN[2]
#FW = IDN[3]

scopeTypeCheck = list(model)
if scopeTypeCheck[3] == "-":
    generation = "IVX"
else:
    generation = "IVnotX"
del IDN, scopeTypeCheck, model

##############################################################################################################################################################################
##############################################################################################################################################################################
## Get the screenshot and save it using above defined function
##############################################################################################################################################################################
##############################################################################################################################################################################

KsInfiniiVisionX.query(':SYSTEM:DSP "";*OPC?') # Turns of previously displayed (non-error) message

KsInfiniiVisionX.write(":HARDcopy:INKSaver OFF") # Inverted back ground or not
# Ask scope for screenshot in png format
if generation == "IVnotX":
    KsInfiniiVisionX.write(":DISPlay:DATA? PNG,SCReen,COLor") # The older InfiniiVisions have 3 parameters
elif generation == "IVX":
    KsInfiniiVisionX.write(":DISPlay:DATA? PNG,COLor") # The newer InfiniiVision-Xs do not have the middle parameter above

## Get screen image as a binary file
my_image = KsInfiniiVisionX.read_raw()
    ##  Can close connection to scope now
## Interpret Header and Return Raw DATA
my_image = binblock_raw(my_image)

## Define file name
filename = BASE_DIRECTORY + BASE_FILE_NAME + ".png"

## Save Screen Image to File
target = open(filename,'wb') # wb means open for writing in binary; can overwrite
target.write(my_image)
target.close()

del my_image, filename, target

## Close conenctioon to scope
KsInfiniiVisionX.clear() # Clear scope communications interface
KsInfiniiVisionX.close() # Close communications interface to scope
print "Done."