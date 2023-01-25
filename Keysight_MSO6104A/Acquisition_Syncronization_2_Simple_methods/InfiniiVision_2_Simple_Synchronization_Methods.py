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

## Import python modules - Not all of these are used in this program; provided for reference
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
## This script should work for all InfiniiVision and InfiniiVision-X oscilloscopes:
## DSO5000A, DSO/MSO6000A/L, DSO/MSO7000A/B, DSO/MSO-X2000A, DSO/MSO-X3000A/T, DSO/MSO-X4000A, DSO/MSO-X6000A

##############################################################################################################################################################################
##############################################################################################################################################################################
## DEFINE CONSTANTS
##############################################################################################################################################################################
##############################################################################################################################################################################

## Initialization constants
VISA_ADDRESS = "USB0::0x0957::0x17A0::MY51500437::0::INSTR" # Get this from Keysight IO Libraries Connection Expert #Note: sockets are not supported in this revision of the script, and pyVisa 1.6.3 does not support HiSlip
GLOBAL_TOUT =  10000 # IO time out in milliseconds

## Save Locations
BASE_FILE_NAME = "my_data"
BASE_DIRECTORY = "C:\\Users\\Public\\"
    ## IMPORTANT NOTE:  This script WILL overwrite previously saved files!

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define functions to synchronize InfiiVision Oscilloscopes
##############################################################################################################################################################################
##############################################################################################################################################################################

## Define a simple and fast function utilizing the blocking :DIGitize command in conjunction with *OPC?
def method1():
    KsInfiniiVisionX.timeout =  100000 # Time in milliseconds (PyVisa uses ms) to wait for the scope to arm, trigger, finish acquisition, and finish any processing.
        ## Note that this is a property of the device interface, KsInfiniiVisionX.

    print "Acquiring signal(s)...\n"
    try: # Set up a try/except block to catch a possible timeout and exit.
        KsInfiniiVisionX.query(":DIGitize;*OPC?") # Acquire the signal(s) with :DIGItize (blocking) and wait until *OPC? comes back with a one.
        print "Signal acquired.\n"
    except Exception: # Catch a possible timeout and exit.
        print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Properly closing scope connection and exiting script.\n"
        KsInfiniiVisionX.clear() # Clear scope communications interface; a device clear also aborts a digitize.
        KsInfiniiVisionX.close() # Close communications interface to scope
        sys.exit("Exiting script.")
    KsInfiniiVisionX.timeout =  10000 # Reset timeout back to what it was, 10 seconds.

    ## Benefits of this method:
        ## Fastest, compact
        ## Only way for Average Acquisition mode:
            ## The :SINGle does not do a complete average, and counting triggers in :RUN is much too slow
        ## Allows for synchronization with math functions
        ## Don't have to deal with the status registers, which can be confusing.
    ## Drawbacks of this method:
        ## Requires a well-chosen, hard-set timeout that will cover the time to arm, trigger,
            ## and finish acquisition.
        ## Requires Exception handling and a device clear for a possible timeout (no trigger event)
        ## Since :DIGitize is a "specialized form of the :RUN" command, on these scope, that results in:
            ## the sample rate MAY be reduced from using :SINGle - usually at longer time scales
            ## typically only acquires what is on screen, though at the fastest time scales, more than on screen data will be acquired.
            ## Thus, for max memory and max sample rate, use method2, which uses :SINGLE.  However,
            ## for max throughput, use this method.
    ## How it works:
        ## The :DIGitize command is a blocking command, and thus, all other SCPI commands are blocked until
            ## :DIGitize is completely done.  This includes any subsequent processing that is already set up,
            ## such as math, jitter separation, measurements.  Key Point: the *OPC? query is appended to
            ## :DIGitize with a semi-colon (;), which essentially ties it to the same thread in the parser.
            ## It is immediately dealt with once :DIGitize finishes and gives a “1” back to the script, allowing the script to move on.
    ## Other Notes:
        ## If you DO NOT know when a trigger will occur, you will need to (should) set a very long time out.
        ## The timeout will need to be (should be) adjusted before and after the :DIGitize operation,
            ## though this is not absolutely required.
        ## A :DIGitize can be aborted with a device clear: KsInfiniiVisionX.clear()

## Define a function using the non-blocking :SINGle command and polling on the Operation Status Condition
def method2():

    ## Define "mask" bits and completion criterion.
    ## Mask bits for Run state in the Operation Status Condition (and Event) Register
         ## This can be confusing.  In general, refer to Programmer's Guide chapters on Status Reporting, and Synchronizing Acquisitions
         ## Also see the annotated screenshots included with this sample script.
    RUN_BIT = 3 # The run bit is the 3rd bit.  If it is high, the scope is in a RUN state, i.e. not done.
    RUN_MASK = 1<<RUN_BIT  # This basically means:  2^3 = 8, or rather, in Python 2**3 (<< is a left shift); this is used later to
        ## "unmask" the result of the Operation Status Event Register as there is no direct access to the RUN bit.

    ## Completion criteria
    ACQ_DONE = 0 # Means the scope is stopped
    ACQ_NOT_DONE = 8 # This is the 4th bit of the Operation Status Condition (and Event) Register.  The registers are binary and start counting at zero, thus the 4th bit is bit number 3, and 2^3 = 8.
        ## This is either High (running = 8) or low (stopped and therefore done with acquisition = 0).

    MAX_TIME_TO_WAIT = 100 # Time in seconds to wait for the scope to arm, trigger, and finish acquisition.
        ## Note that this is NOT a property of the deice interface, KsInfiniiVisionX, but rather some constant in the script to be used later with
            ## the Python module "time," and will be used with time.clock().

    print "Acquiring signal(s)...\n"
    KsInfiniiVisionX.write("*CLS") # Clear all registers; sets them to 0; This could be concatenated with :SINGle command two lines below line to speed things up a little like this -> KsInfiniiVisionX.write("*CLS;:SINGle")
    StartTime = time.clock() # Define acquisition start time; This is in seconds.
    KsInfiniiVisionX.write(":SINGle") # Beigin Acquisition with non-blocking :SINGle command
    ## KsInfiniiVisionX.write("*CLS;:SINGle") # Recommended to concatenate these together for repeated acquisition using this method as it goes slightly faster; consider using method1 instead if max throughput is desired
    Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?")) # Immediately ask scope if it is done with the acquisition via the Operation Status Condition (not Event) Register.
        ## The Condition register reflects the CURRENT state, while the EVENT register reflects the first event that occurred since it was cleared or read, thus the CONDTION register is used.
    Acq_State = (Status & RUN_MASK) # Bitwise AND of the Status and RUN_MASK.  This exposes ONLY the 3rd bit, which is either High (running = 8) or low (stopped and therefore done with acquisition = 0)

    ## Poll the scope until Acq_State is a one. (This is NOT a "Serial Poll.")
    while Acq_State == ACQ_NOT_DONE and (time.clock() - StartTime <= MAX_TIME_TO_WAIT): # This loop is never entered if the acquisition completes immediately; Exits if Status == 1 or MAX_TIME_TO_WAIT exceeded
        time.sleep(.1) # Pause 100 ms to prevent excessive queries
        Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?")) # Read status byte
        Acq_State = (Status & RUN_MASK)
        ## Loop exists when Acq_State != NOT_DONE, that is, it exits the loop when it is DONE
    if Acq_State == ACQ_DONE: # Acquisition fully completed
        print "Signal acquired.\n"
    else: # Acquisition failed for some reason
        print "Max wait time exceeded."
        print "This can happen if there was not enough time to arm the scope, there was no trigger event, or the scope did not finish acquiring."
        print "Visually check the scope for a trigger, adjust settings accordingly.\n"
        print "Properly closing scope connection and exiting script.\n"
        KsInfiniiVisionX.clear() # Clear scope communications interface
        KsInfiniiVisionX.write(":STOP") # Stop the scope
        KsInfiniiVisionX.close() # Close communications interface to scope
        sys.exit("Exiting script.")

    ## Benefits of this method:
        ## Don't have to worry about interface timeouts
        ## Easy to expand to know when scope is armed, and triggered
    ## Drawbacks of this method:
        ## Slow
        ## Does NOT work for Average Acquisition mode
            ## The :SINGle does not do a complete average, and counting triggers in :RUN is much too slow
        ## Can't be used effectively for synchronizing math functions
            ## It can be done by applying an additional hard coded wait after the acquisition is done.  At least 200 ms is suggested, more may be required.
        ## Still need some maximum timeout (here MAX_TIME_TO_WAIT), ideally, or the script will sit in the while loop forever if there is no trigger event
        ## Max time out (here MAX_TIME_TO_WAIT) must also account for any processing done
        ## Max time out (here MAX_TIME_TO_WAIT) must also account for time to arm the scope and finish the acquisition
    ## How it works:
        ## Pretty well explained in line; see annotated screenshots. Basically:
            ## What really matters is the RUN bit in the Operation Condition (not Event) Register.  This bit changes based on the scope state.
            ## If the scope is running, it is high (8), and low (0) if it is stopped.
            ## The only way to get at this bit is with the :OPERation:CONDition? query.  The Operation Condition Register can reflect states
            ## for other scope properties, for example, if the scope is armed, thus it can produce values other than 0 (stopped) or 8 (running).
            ## To handle that, the result of :OPERation:Condition? is logically ANDed (& in Python) with an 8.  This is called "unmasking."
            ## Here, the "unmasking" is done in the script.  On the other hand, it is possible to "mask" which bits get passed to the
            ## summary bit to the next register below on the instrument itself.  However, this method it typically only used when working with the Status Byte,
            ## and not used here.
            ## Why 8 = running = not done?
                ## The Run bit is the 4th bit of the Operation Status Condition (and Event) Registers.
                ## The registers are binary and start counting at zero, thus the 4th bit is bit number 3, and 2^3 = 8, and thus it returns an 8 for high and a 0 for low.
            ## Why the CONDITION and NOT the EVENT register?
                ## The Condition register reflects the CURRENT state, while the EVENT register reflects the first event that occurred since it was cleared or read,
                ## thus the CONDTION register is used.

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

## Clear the instrument bus
KsInfiniiVisionX.clear()

##############################################################################################################################################################################
##############################################################################################################################################################################
## Main code
##############################################################################################################################################################################
##############################################################################################################################################################################

###############################################################################
## Setup scope
KsInfiniiVisionX.write(":STOP") # Scope always should be stopped when making changes.
## Whatever is needed

## For this example, the scope will be forced to trigger on the (power) LINE voltage so something happens
KsInfiniiVisionX.write(":TRIGger:SWEep NORMal") # Always use normal trigger sweep, never auto.
KsInfiniiVisionX.query(":TRIGger:EDGE:SOURce LINE;*OPC?") # This line simply gives the scope something to trigger on

###############################################################################
## Acquire Signal

## Choose method1 or method2
## There is no a-priori reason to do this as a Python function
method1()

###############################################################################
## Do Something with data... save, export, additional analysis...

## For example, make a peak-peak voltage measurement on channel 1:
Vpp_Ch1 = str(KsInfiniiVisionX.query("MEASure:VPP? CHANnel1")).strip("\n") # The result comes back with a newline, so remove it with .strip("\n")
print "Vpp Ch1 = " + Vpp_Ch1 + " V\n"

###############################################################################

##############################################################################################################################################################################
##############################################################################################################################################################################
## Done - cleanup
##############################################################################################################################################################################
##############################################################################################################################################################################

KsInfiniiVisionX.clear() # Clear scope communications interface
KsInfiniiVisionX.close() # Close communications interface to scope

print "Done."