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

## Import Python modules - Not all of these are used in this program; provided for reference
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
## pyvisa 1.8 is used
## Windows 7 Enterprise, 64 bit (has implications for time.clock if ported to unix type machine, use timt.time instead)

## HiSlip and Socket connections not supported

## DESCRIPTION OF FUNCTIONALITY
## This script can log an indefinite number of measurements, trigger times, and screenshots from any InfiniiVision or InfiniiVision oscilloscope indefinitely. It is fully synchronized.
## This is NOT gapless recording:
    ## Scope triggers, fills buffer, makes measurement(s), dead time occurs, repeat.  Rates can be as fast as 10s of Hz.
## User can define measurements and oscilloscope setup, OR, manually set up the oscilloscope and measurements, and use those, OR any combination.
## This script saves the data at the end of the of the acquisition cycle.  This is good for best through put, but, if something goes wrong in the middle, the
    ## data can be lost.  A separate, though near identical script is/will be provide separately that saves data after each acquisition cycle at a small hit to
    ## through put.  It has/will have the same name, but “SAVE-DURING-ACQUISITION” is at the end of the file name.
    ## However, robust error checking and handling will try to save the data in all failure cases, except for running out of physical memory.
## This script is not really intended to be modified, but rather used.
## User defined measurements are checked for basic correctness unless they use the ZOOM window or cursor gating.
    ## User should still check that the measurement results actually make sense.  The script will not abort or warn if, for example, a measurement returns 9.9e+37 (infinity)...
## A special mode is included to use the scope as trigger time tag recorder.  This is best used for events occurring at less than 10 Hz, though some scopes and connections can go about 100 Hz.
## In average mode, measurements are not done until all averages are completed.  This is not what the scope does from the front panel, but is the "right way" to do it.
## XT, Roll, Equivalent time, Mask, Segmented memory, and certain other modes are not supported.  An alternate script is provided for segmented memory.
## Math functions are supported.
## There are three addenda the very end of the script.
    ## The first shows how to re-import the data back into Python.
    ## The second describes the basic structure of this script.
    ## The third shows how to do a few of the more complex measurements, define custom thresholds, and use the ZOOM window or cursors (where applicable) to gate measurements.

## This script should work for all InfiniiVision and InfiniiVision-X oscilloscopes:
## DSO5000A, DSO/MSO6000A/L, DSO/MSO7000A/B, DSO/MSO-X2000A, DSO/MSO-X3000A/T, DSO/MSO-X4000A, DSO/MSO-X6000A
## A firmware check is included.

## INSTRUCTIONS
## Use of this script is fairly straightforward.  Edit in the desired constants and measurements just below.  Each is well described as to the functionality.
## The user can define the base file name and the directory to where the data will be saved. This script WILL OVERWRITE previously saved data.
## The main thing is that the user can either:
    ## 1. Define as many measurements via the script as are needed.  Here, the user must additionally define a header and put together a trivial string telling
        ## the script which of defined the measurements to use, though the header should match...
## Or
    ## 2. Just enable measurements on the scope, and it the script will take care of the rest, including the header.
## ALWAYS do some test runs to ensure you are getting what you want, that the data is in a usable format, and that the measurement results make sense.
    ## If the measurement results don't make sense, set up the measurements manually on the scope and ensure that they do.
        ## This can be caused by the waveforms not being well displayed (i.e. not a big blob), the channel(s) being off or improperly scaled,
        ## or a poor choice of trigger resulting in an improper part of the waveform being captured.

##############################################################################################################################################################################
##############################################################################################################################################################################
## DEFINE CONSTANTS
##############################################################################################################################################################################
##############################################################################################################################################################################

##############################################################################################################################################################################
## Save Locations and format

BASE_FILE_NAME = "my_data"
BASE_DIRECTORY = "C:\\Users\\Public\\"
    ## IMPORTANT NOTE:  This script WILL overwrite previously saved files!  It will error out if the file is open. close it and manually run that line of code.
SAVE_FORMAT = "NUMPY" # "CSV" or "NUMPY"
    ## CSV is easy to work with and can be opened in pretty much anything, e.g. Microsoft XL, but ti is slow
    ## NUMPY is the numpy package binary format, really only good for re-importing into Python, but much faster than CSV.  It IS possible to make this work for other programs though...
        ## A csv header file is separately created for NUMPY saves (no data)
    ## Examples of re-importing into Python are given for both in Adendum 2
SAVE_TRIGGER_TIME_STAMPS_SEPARATELY = "NO" # "YES" or "NO", but always on for USE_AS_TRIGGER_TIME_RECORDER_ONLY = "YES", creates a second file with just trigger time stamps, CSV format only

GET_SCREENSHOT = "NO" # "EVERY, "NO", "FIRST", "LAST", or "FIRSTANDLAST"
    ## Gets a screenshot and saves it to disk in png format, as per setting
    ## Hurts throughput.  Not compatible with  USE_AS_TRIGGER_TIME_RECORDER_ONLY = "YES"
INVERT_BACKGROUND = "YES" # "YES or "NO"
    ## Is the scope background  for screenshots, black (NO) or white (YES)?

##############################################################################################################################################################################
## Scope Connection constants
SCOPE_VISA_ADDRESS = "USB0::2391::2048::MY51500437::0::INSTR" # Get this from Keysight IO Libraries Connection Expert #Note: sockets are not supported in this revision of the script, and pyVisa 1.6.3 does not support HiSlip
GLOBAL_TOUT =  10000 # IO time out in milliseconds - this is not the acquisition time out

##############################################################################################################################################################################
## Scope Setup constants
SCOPE_SETUP_METHOD = "AS_IS" # "SCRIPT" or "AS_IS"
    ## AS_IS:  manually set up the oscilloscope from the front panel, and the script will use this configuration. This is very easy…
    ## SCRIPT: user must write some mode code in the script.  An example is provided for using the probe compensation signal with a  probe.
    ## Both can use either measurement method described below.

TRIGGER_SWEEP   = "NORMal" # "NORMal" or "AUTO"
    ## NORMal: oscilloscope only triggers if there is a true trigger event
    ## AUTO: rather than possibly time out, on no trigger event, the oscilloscope can internally force a trigger, and make measurements anyway.
        ## Note that with Auto mode, hardware defined trigger holdoff does not work when there is no trigger event.
        ## For DC signals, there is no way to trigger directly on the signal itself, thus AUTO sweep is typically recommended. One can also feed the scope some other signal to trigger on...

SCOPE_TRIGGER_HOLDOFF = "MIN" # "MIN" or a number without quotes, e.g. 11e-6; this would have units of seconds
    ## This prevents the scope from re-arming, not from accepting another trigger. To have it basically not accept a trigger, put the trigger position at the exact left of the screen; all of the data will be post trigger.
    ## Note that with Auto trigger sweep, this hardware defined trigger holdoff does not work when there is no trigger event.

LOCK_SCOPE = "YES" # "YES" or "NO"
    ## Locks the oscilloscope front panel so it cannot be adjusted/messed up  during run… always unlocked in most failure cases or at end of script.
    ## Not unlocked in failure cases such as power loss or tripping over the USB cord and thus breaking the connection.
    ## If oscilloscope is locked… re-run the script (may need to reset Python) with this set to NO….

##############################################################################################################################################################################
## Run Control constants

TIME_TO_TRIGGER = 10 # Time in seconds
    ## While the script calculates a general time out for the given setup, it cannot know when a trigger event will occur.  Thus, the user must still set this value.
    ## This time is in addition to the calculated minimum timeout... so, if a scope might take say, 1 us to arm and acquire data,
        ## the signal might take 100 seconds before it occurs... this accounts for that.

RUN_CONTROL_BY_TIME_OR_NUMBER = "NUMBER" # "TIME" or "NUMBER" - stop after a set number of acquisitions or a set amount of time
NUMBER_ACQUISITIONS = 100 # Integer; number of times to trigger, acquire data, and retrieve measurements
## Or:
TIME_TO_RUN = 60 # seconds, Minimum is 10 seconds - for how long to trigger, acquire data, and retrieve measurements

SYNCH_METHOD = "FAST" # "FAST" or "HIGH_SR"
    ## FAST: fastest method, MAY result is lower sampling rate in some cases.  Only method for average acquisition mode (this is taken care of) and math functions.
    ## HIGH_SR: slower synchronization method as the oscilloscope is polled every 100 ms, but can result in a higher sample rate in some cases
    ## What else can affect throughput?
        ## The timebase settings.  The scope can never go faster than the timebase and delay settings allow.
        ## The signal itself.  Even if the scope is at a fast timebase, the throughput can be very slow if there signal of interest only occurs rarely.
        ## The scope's internal programming bus.  The scopes take about 10 ms to parse a command (not necessarily do it).  This puts a best case limit around 100 Hz or so.
        ## The number of measurements and MEAS_METHOD.  If MEAS_METHOD is scope, it can sometimes take a little longer (especially if there are only a few measurements) as there is actually more data to return.
        ## The actual communications interface.  USB is generally fastest.
    ## To test best case throughput, basically set up the scope/script the way it will be used, but instead of the real signal, use a 10 MHz sine or square wave to give the scope something fast to trigger on.

ACQUISITION_TIMEOUT_BEHAVIOR = "SAVE_AND_ABORT" # "SAVE_AND_ABORT" or "TRY_AGAIN"

PAUSE_BETWEEN_ACQUISISTIONS = "NO" # "YES" or "NO"
    ## Simply pauses the script based on the computer's clock before initiating a new acquisition.  To be clear, this is essentially a delay before the scope begins to arm.
    ## The first acquisition is not delayed.
TIME_TO_PAUSE = 1 # Seconds, float or int

##############################################################################################################################################################################
## Measurement methods/definitions

MEAS_METHOD = "SCRIPT" # "SCRIPT" or "SCOPE"
    ## SCRIPT: uses the below defined measurements.
        ## Find where in the script to do this by searching for (Ctrl f): ##SCOPE_SETUP_BY_SCRIPT
        ## Benefits: Highly flexible as thresholds, zoom windows/gates can be adjusted per measurement, and not limited by however many measurements the oscilloscope can display at once.
        ## Drawbacks: user may need to refer to programmer’s guide just a little, measurement results do not show up on screen, must defined a few other trivial things eblow.
        ## See addendum 1 at very end of script for examples of more complex measurements
        ## Programmer’s guide at: http://www.keysight.com/find/products/   <- add scope model number (no spaces or hyphens, e.g. http://www.keysight.com/find/products/MSOX3054A
    ## SCOPE: uses the measurements defined on the scope
        ## Benefits: easy
        ## Drawback: the exact opposite of the benefits for MEAS_METHOD = "SCRIPT

## Define measurements for MEAS_METHOD = “SCRIPT”
M1 = ":MEASure:VMAX? CHANnel1"
M2 = ":MEASure:FREquency? CHANnel1"
## Keep adding measurements as desirer... They can really be named whatever is desired… they just need to match what is defined below for MEASURE_LIST
## See addendum at very end of script for examples of more complex measurements

## Define list of measurements and header for MEAS_METHOD = “SCRIPT”
MEASURE_LIST = [M1] # Just keep making this list longer... e.g. 4 measurements would be: [M1,M2,M3,M4] and so on... They can really be named whatever is desired… they just need to match what is defined above.
## Can even have it skip defined measurements, e.g. M1-M10 are defined, but user only wants to do M2 and M3 -> MEASURE_LIST = [M2,M3], just be sure the header below matches

SCOPE_MEASUREMENT_HEADER = "Vpeak-peak CH1 (V)"
#SCOPE_MEASUREMENT_HEADER = "Vpeak-peak CH1 (V),Frequency CH1 (Hz), Vmin CH1 (V), Delay CH1-CH3 (s)" # <- example of a longer header
    ## Again, just keep adding to this.  One name per measurement, followed by a comma, except for the last one

ENABLE_PRECISION_MODE = "NO" # "YES" or "NO"
    ## On some scopes it is possible to enable a "precision" record which increases the number of points the measurements are made on:
    ## For X2000A, X3000A/T, X4000A, there is no precision mode; it is essentially always on, and is about ~65 kPts long
    ## For DS05000A and DSO/MSO6000A/L, there is a precision mode of 10 kPts, otherwise the default length is 1000 Pts
    ## For DSO/MSO7000A/B, there is a precision mode of ~128 kPts, otherwise the default length is 1000 Pts
    ## For X6000A, there is a precision mode that is configurable from 100,000 to 1,000,000 Pts, otherwise the default is 65 kPts
    ## Precision mode affects math waveforms as well, and can slow down the throughput.
    ## Precision mode is not compatible with Average or High Resolution acquisition modes. Use of these modes overrides this setting.
    ## Data must be fully on screen for this to have an effect.
    ## This will hurt the throughput.
    ## This will be done in both cases of SCOPE_SETUP_METHOD = SCOPE or SCRIPT
PRECISION_LENTGH_X6000A_ONLY = 1000000 # an integer, not a float, from 100000 (100k)to 1000000 (1M)

USE_AS_TRIGGER_TIME_RECORDER_ONLY = "NO" # "YES" or "NO"
    ## No measurements are performed.
    ## Only saves records trigger times in csv format. These are always saved.
    ## Best use case is for more rarely occurring signals, ~100 Hz best case.  For more rapidly occurring signals, use segmented memory...
    ## Makes the following settings changes:
        ## Sets SYNCH_METHOD = "FAST"
        ## Sets Acquisition mode to NORMAL.
        ## Sets timebase to something very fast (5 ns/Div) (5 ns covers all scopes) and center screen position (zero delay)
        ## Sets TRIGGER_SWEEP = "NORMal"
        ## Disables measurements on the scope
        ## Disables the zoom window
        ## Disables "precision mode" where applicable
        ## Does not set minimum trigger holdoff as there are some cases where this may be desired...
        ## Turns off lister, serial decode (serial trigger ok), and math functions if they are on and SCOPE_SETUP_METHOD = "AS_IS"

##############################################################################################################################################################################
## Measurement and throughput reporting

REPORT_MEASUREMENT_STATISTICS = "YES" # "YES or "NO" # This is only done at the end, after all acquisitions complete.
REPORT_THRUPUT_STATISTICS = "YES" # "YES or "NO" # This is only done at the end, after all acquisitions complete.
NUMBER_BINS = "DEFAULT" # "DEFAULT" or an integer > 10.  DEFAULT is 10, and anything lower will be set to 10.

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define function a user modifiable function to do the scope setup by the script
##############################################################################################################################################################################
##############################################################################################################################################################################

##SCOPE_SETUP_BY_SCRIPT
## This is where the user should modify the scope setup for SCOPE_SETUP_METHOD = "SCRIPT"

def Scope_Setup_by_Script():
    ## The order shown here should be followed...

    ## Leave these first two alone...
    KsInfiniiVisionX.query("*RST;*OPC?") # Reset scope
    KsInfiniiVisionX.write(":STOP") # Stop scope before making changes

    ## Set acquisition type
    KsInfiniiVisionX.write(":ACQuire:TYPE NORMal")

    ## Setup timebase - Set them in this order
    KsInfiniiVisionX.write(":TIMebase:MODE MAIN")
    KsInfiniiVisionX.write(":TIMebase:REFerence CENTer")
    KsInfiniiVisionX.write(":TIMebase:SCALe 200e-6")
    KsInfiniiVisionX.write(":TIMebase:POSition 0")
    KsInfiniiVisionX.query("*OPC?")

    ## Turn channels on/off
    KsInfiniiVisionX.write(":CHANnel1:DISPlay 1") # Turn on channel1
    KsInfiniiVisionX.write(":CHANnel2:DISPlay 0") # Turn off the other channels (though they would be off after a reset)
    KsInfiniiVisionX.write(":CHANnel3:DISPlay 0")
    KsInfiniiVisionX.write(":CHANnel4:DISPlay 0")

    ## Setup channel(s)
    ## User should attach any probes...
    ## Adjust channel skew really anytime - note: skew is software based, so it can mess up parallel pattern triggering.
    KsInfiniiVisionX.write(":CHANnel1:IMPedance ONEMeg") # Set Impedance
    KsInfiniiVisionX.write(":CHANnel1:PROBe X10") # Set probe attenuation ratio (not dB)
    ## Do any other probe commands here.
    KsInfiniiVisionX.write(":CHANnel1:SCALe 0.5") # Set scale AFTER defining impedance and probe; many probes will ID themselves, depending on scope model
    KsInfiniiVisionX.query(":CHANnel1:OFFSet 1.25;*OPC?") # set offset AFTER setting vertical scale

    ## Setup Trigger
    ## Note that the trigger sweep is setup later in this particular script...
    KsInfiniiVisionX.write(":TRIGger:MODE EDGE")
    KsInfiniiVisionX.write(":TRIGger:EDGE:SOURce CHANnel1") # Set source for edge trigger
    KsInfiniiVisionX.write(":TRIGger:EDGE:COUPling DC")
    KsInfiniiVisionX.write(":TRIGger:EDGE:SLOPe POSitive")
    KsInfiniiVisionX.write(":TRIGger:EDGE:LEVel 1") # Set level last
    KsInfiniiVisionX.query("*OPC?")

    ## Add other stuff, such as math...

    ## Do error check
    Setup_Err = ErrCheck()
    if len(Setup_Err) == 0:
        sys.stdout.write("Setup completed without error.")
        del Setup_Err
    else:
        IVScopeSafeExitCustomMessage("Setup has errors.  Properly closing scope and exiting script.")

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define functions to synchronize InfiniiVision Oscilloscopes
## Refer to the sample script InfiniiVision_2_Simple_Synchronization_Methods.py for comments/documentation
##############################################################################################################################################################################
##############################################################################################################################################################################

def method1(TO, SMR, SMH):
    try:
        KsInfiniiVisionX.query(":DIGitize;*OPC?")
        fin_time = time.clock()
        return fin_time

    except Exception:
        if ACQUISITION_TIMEOUT_BEHAVIOR == "SAVE_AND_ABORT":
            print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Properly closing scope connection, saving data, and exiting script.\n"
            print "Visually check the scope for a trigger, adjust settings accordingly.\n"
            if int(len(SMR)) == 0:
                print "No data acquired.  Not saving anything.  Properly closing scope."
                KsInfiniiVisionX.clear()
                KsInfiniiVisionX.write(":SYSTem:LOCK 0")
                KsInfiniiVisionX.write(":STOP")
                KsInfiniiVisionX.close()
                sys.exit("Exiting script.")
            else:
                KsInfiniiVisionX.clear()
                KsInfiniiVisionX.write(":SYSTem:LOCK 0")
                KsInfiniiVisionX.write(":STOP")
                print "Forcing a trigger to properly correct trigger time stamps."
                KsInfiniiVisionX.write(":TRIGger:SWEep AUTO")
                KsInfiniiVisionX.query(":DIGitize;*OPC?")
                KsInfiniiVisionX.write(":TRIGger:SWEep " + str(TRIGGER_SWEEP))
                SRP = Get_SR_Points()
                SMR = Correct_Time_Stamps(SMR)
                KsInfiniiVisionX.close()
                Save_Data(SMR, SMH)
                do_stats(SMR, SMH, SRP)
                print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Properly closing scope connection, saving data, and exiting script.\n"
                print "Visually check the scope for a trigger, adjust settings accordingly.\n"
                print "Some data was captured and saved."
                sys.exit("Exiting script.")
        else:
            print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Trying again once with twice the timeout, which will be reset...\n"
            KsInfiniiVisionX.timeout = TO*2.0
            try:
                KsInfiniiVisionX.clear()
                #KsInfiniiVisionX.query(":TRIGger:SWEep AUTO;*OPC?")
                KsInfiniiVisionX.query(":DIGitize;*OPC?")
                fin_time = time.clock()
                print "Success."
                #KsInfiniiVisionX.query(":TRIGger:SWEep " + str(TRIGGER_SWEEP) + ";*OPC?")
                KsInfiniiVisionX.timeout = TO
                return fin_time
            except Exception:
                if int(len(SMR)) == 0:
                    print "No data acquired.  Not saving anything.  Properly closing scope."
                    KsInfiniiVisionX.clear()
                    KsInfiniiVisionX.write(":SYSTem:LOCK 0")
                    KsInfiniiVisionX.write(":STOP")
                    KsInfiniiVisionX.close()
                    sys.exit("Exiting script.")
                else:
                    KsInfiniiVisionX.clear()
                    KsInfiniiVisionX.write(":SYSTem:LOCK 0")
                    KsInfiniiVisionX.write(":STOP")
                    print "Forcing a trigger to properly correct trigger time stamps."
                    KsInfiniiVisionX.write(":TRIGger:SWEep AUTO")
                    KsInfiniiVisionX.query(":DIGitize;*OPC?")
                    KsInfiniiVisionX.write(":TRIGger:SWEep " + str(TRIGGER_SWEEP))
                    SRP = Get_SR_Points()
                    SMR = Correct_Time_Stamps(SMR)
                    KsInfiniiVisionX.close()
                    Save_Data(SMR, SMH)
                    do_stats(SMR, SMH, SRP)
                    print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Properly closing scope connection, saving data, and exiting script.\n"
                    print "Visually check the scope for a trigger, adjust settings accordingly.\n"
                    print "Some data was captured and saved."
                    sys.exit("Exiting script.")

def method2(TO, SMR, SMH):
    RUN_BIT = 3
    RUN_MASK = 1<<RUN_BIT
    ACQ_DONE = 0
    ACQ_NOT_DONE = 8
    MAX_TIME_TO_WAIT = TO/1000.0
    StartTime = time.clock()
    KsInfiniiVisionX.write("*CLS;:SINGle")
    Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?"))
    Acq_State = (Status & RUN_MASK)
    while Acq_State == ACQ_NOT_DONE and (time.clock() - StartTime <= MAX_TIME_TO_WAIT):
        time.sleep(.1)
        Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?"))
        Acq_State = (Status & RUN_MASK)
    if Acq_State == ACQ_DONE:
        fin_time = time.clock()
        return fin_time
    else:
        if ACQUISITION_TIMEOUT_BEHAVIOR == "SAVE_AND_ABORT":
            print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Properly closing scope connection, saving data, and exiting script.\n"
            print "Visually check the scope for a trigger, adjust settings accordingly.\n"
            if int(len(SMR)) == 0:
                    print "No data acquired.  Not saving anything.  Properly closing scope."
                    KsInfiniiVisionX.clear()
                    KsInfiniiVisionX.write(":SYSTem:LOCK 0")
                    KsInfiniiVisionX.write(":STOP")
                    KsInfiniiVisionX.close()
                    sys.exit("Exiting script.")
            else:
                KsInfiniiVisionX.clear()
                KsInfiniiVisionX.write(":SYSTem:LOCK 0")
                KsInfiniiVisionX.write(":STOP")
                print "Forcing a trigger to properly correct trigger time stamps."
                KsInfiniiVisionX.write(":TRIGger:SWEep AUTO")
                KsInfiniiVisionX.write(":STOP;*CLS;:SINGle")
                Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?"))
                Acq_State = (Status & RUN_MASK)
                reStartTime = time.clock()
                while Acq_State == ACQ_NOT_DONE and (time.clock() - reStartTime <= MAX_TIME_TO_WAIT):
                    time.sleep(.1)
                    Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?"))
                KsInfiniiVisionX.write(":TRIGger:SWEep " + str(TRIGGER_SWEEP))
                SRP = Get_SR_Points()
                SMR = Correct_Time_Stamps(SMR)
                KsInfiniiVisionX.close()
                Save_Data(SMR, SMH)
                do_stats(SMR, SMH, SRP)
                print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Properly closing scope connection, saving data, and exiting script.\n"
                print "Visually check the scope for a trigger, adjust settings accordingly.\n"
                print "Some data was captured and saved."
                sys.exit("Exiting script.")
        else:
            print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Trying again once with twice the timeout, which will be reset...\n"
            MAX_TIME_TO_WAIT = TO/1000*2.0
            KsInfiniiVisionX.write(":STOP;*CLS;:SINGle")
            Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?"))
            Acq_State = (Status & RUN_MASK)
            reStartTime = time.clock()
            while Acq_State == ACQ_NOT_DONE and (time.clock() - reStartTime <= MAX_TIME_TO_WAIT):
                time.sleep(.1)
                Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?"))
                Acq_State = (Status & RUN_MASK)
            if Acq_State == ACQ_DONE:
                fin_time = time.clock()
                print "Success."
                return fin_time
            else:
                print "The acquisition timed out again, most likely due to no trigger, or improper setup causing no trigger. Properly closing scope connection, saving data, and exiting script.\n"
                print "Visually check the scope for a trigger, adjust settings accordingly.\n"
                if int(len(SMR)) == 0:
                    print "No data acquired.  Not saving anything.  Properly closing scope."
                    KsInfiniiVisionX.clear()
                    KsInfiniiVisionX.write(":SYSTem:LOCK 0")
                    KsInfiniiVisionX.write(":STOP")
                    KsInfiniiVisionX.close()
                    sys.exit("Exiting script.")
                else:
                    KsInfiniiVisionX.clear()
                    KsInfiniiVisionX.write(":SYSTem:LOCK 0")
                    KsInfiniiVisionX.write(":STOP")
                    print "Forcing a trigger to properly correct trigger time stamps."
                    KsInfiniiVisionX.write(":TRIGger:SWEep AUTO")
                    KsInfiniiVisionX.write(":STOP;*CLS;:SINGle")
                    Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?"))
                    Acq_State = (Status & RUN_MASK)
                    reStartTime = time.clock()
                    while Acq_State == ACQ_NOT_DONE and (time.clock() - reStartTime <= MAX_TIME_TO_WAIT):
                        time.sleep(.1)
                        Status = int(KsInfiniiVisionX.query(":OPERegister:CONDition?"))
                    KsInfiniiVisionX.write(":TRIGger:SWEep " + str(TRIGGER_SWEEP))
                    SRP = Get_SR_Points()
                    SMR = Correct_Time_Stamps(SMR)
                    KsInfiniiVisionX.close()
                    Save_Data(SMR, SMH)
                    do_stats(SMR, SMH, SRP)
                    print "The acquisition timed out, most likely due to no trigger, or improper setup causing no trigger. Properly closing scope connection, saving data, and exiting script.\n"
                    print "Visually check the scope for a trigger, adjust settings accordingly.\n"
                    print "Some data was captured and saved."
                    sys.exit("Exiting script.")

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define a few Python helper functions for the scope
##############################################################################################################################################################################
##############################################################################################################################################################################

## Define a Timebase Reset function
def Scope_Timebase_Reset(TR, TS, TP):
    KsInfiniiVisionX.query(":TIMebase:REFerence " + str(TR) + ";SCALe " + str(TS) + ";POSition " + str(TP) + ";*OPC?")

## Define Error Check function
def ErrCheck():
    myError = []
    ErrorList = KsInfiniiVisionX.query(":SYSTem:ERRor?").split(',')
    Error = ErrorList[0]
    while int(Error)!=0:
        print "Error #: " + ErrorList[0]
        print "Error Description: " + ErrorList[1]
        myError.append(ErrorList[0])
        myError.append(ErrorList[1])
        ErrorList = KsInfiniiVisionX.query(":SYSTem:ERRor?").split(',')
        Error = ErrorList[0]
        myError = list(myError)
    return myError

## Define a descriptive safe exit function
def IVScopeSafeExitCustomMessage(message):
    KsInfiniiVisionX.clear()
    KsInfiniiVisionX.query(":STOP;*OPC?")
    KsInfiniiVisionX.write(":SYSTem:LOCK 0")
    Scope_Timebase_Reset(TimeReference, TimeScale, TimePosition)
    KsInfiniiVisionX.clear()
    KsInfiniiVisionX.close()
    sys.exit(message)

## Define a function to get a screenshot
def Get_Screen(gen,acqN):
    if INVERT_BACKGROUND == "NO":
        KsInfiniiVisionX.write(":HARDcopy:INKSaver OFF")
    else:
        KsInfiniiVisionX.write(":HARDcopy:INKSaver ON")
    if gen == "IVnotX":
        KsInfiniiVisionX.write(":DISPlay:DATA? PNG,SCReen,COLor")
    elif gen == "IVX":
        KsInfiniiVisionX.write(":DISPlay:DATA? PNG,COLor")
    my_image = KsInfiniiVisionX.read_raw()
    my_image = binblock_raw(my_image)
    filename = BASE_DIRECTORY + BASE_FILE_NAME + "_AcqNumber" + str(acqN) + ".png"
    target = open(filename,'wb')
    target.write(my_image)
    target.close()
    del my_image, filename, target

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define a Function for Binary Data Management for grabbing screenshots
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
## Define a Function to find the sample rate used and the number of points the measurements were made on
##############################################################################################################################################################################
##############################################################################################################################################################################

def Get_SR_Points():
    SR = int(KsInfiniiVisionX.query(":ACQuire:SRATe?"))
    KsInfiniiVisionX.write(":WAVeform:POINts:MODE NORMal")
    P = int(KsInfiniiVisionX.query(":WAVeform:POINts?"))
    return SR, P

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define a Function for Correcting Trigger Time Stamps - this is only used in case of an acquisition timeout
##############################################################################################################################################################################
##############################################################################################################################################################################

def Correct_Time_Stamps(SMR):
    try:

        if type(SMR) == list:
            SMR = np.asarray(SMR, dtype = float)

        ##############################################################################################################################################################################
        ## Find time from trigger to final acquisition point
            ## For properly determining trigger times - somewhat complicated
            ## Currently NOT OK for average mode

        ## Bring data on screen for any initial time base setup
        if ACQ_TYPE != "AVER":
            if TimeReference == ("RIGHt") and (TimePosition < -50.0) and (TimeScale  > 20.0):
                KsInfiniiVisionX.write(":TIMebase:SCALe 50;POSition -50 S") # This ensures that all data will be available in this scenario
            elif TimeReference == ("CENTer") and (TimePosition < -250.0) and (TimeScale  > 20.0):
                KsInfiniiVisionX.write(":TIMebase:SCALe 50;POSition -250 S") # This ensures that all data will be available in this scenario
            elif TimeReference == ("LEFT") and (TimePosition < -450.0) and (TimeScale  > 20.0):
                KsInfiniiVisionX.write(":TIMebase:SCALe 50;POSition -450 S") # This ensures that all data will be available in this scenario
            else:
                KsInfiniiVisionX.write(":TIMebase:SCALe 50")# This ensures that all data will be available in this scenario

        KsInfiniiVisionX.write("WAVeform:POINts MAX") # If using :WAVeform:POINts MAX, be sure to do this BEFORE setting the :WAVeform:POINts:MODE as it will switch it to MAX
        if ACQ_TYPE == "AVER":
            KsInfiniiVisionX.write("WAVeform:POINts:MODE NORMal")
        else:
            KsInfiniiVisionX.write("WAVeform:POINts:MODE RAW")
        #KsInfiniiVisionX.write("WAVeform:POINts MAX") # If using :WAVeform:POINts MAX, be sure to do this BEFORE setting the :WAVeform:POINts:MODE as it will switch it to MAX

        ## Find any channel that is on and acquried data, set the waveform source to that channel
        for ch in range (1,5,1):
            on_off = int(KsInfiniiVisionX.query(":CHANnel" + str(ch) + ":DISPlay?"))
            if on_off == 1:
                Channel_acquired = int(KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel" + str(ch) + ";:WAVeform:POIN?"))
                if Channel_acquired > 0 and on_off == 1:
                    KsInfiniiVisionX.write("WAVeform:SOURce CHANnel" + str(ch))
                    break

        ## Get timing pre-amble data
        Pre = KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',')
        POINTS      = int(Pre[2]) # Gives the scope acquisition mode; this is already doen above in this particular script
        X_INCrement = float(Pre[4]) # Time difference between data points
        X_ORIGin    = float(Pre[5]) # Always the first data point in memory
        X_REFerence = float(Pre[6]) # Specifies the data point associated with x-origin; The x-reference point is the first point displayed and XREFerence is always 0.
            ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.

        ## Reset time base
        Scope_Timebase_Reset(TimeReference, TimeScale, TimePosition)

        LAST_TIME_POINT    = ((POINTS-X_REFerence)*X_INCrement)+X_ORIGin
        TIME_TO_FINISH_ACQ = LAST_TIME_POINT # This must be subtracted from the nominal trigger times

        ##############################################################################################################################################################################
        ## Correct trigger times, as a they are really acquisition done times
        if USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
            SMR = SMR - TIME_TO_FINISH_ACQ
        else:
            SMR[:,1] = SMR[:,1] - TIME_TO_FINISH_ACQ
        return SMR

    except Exception as err:
        print 'Exception: ' + str(err.message) + "\n"
        print 'Exception occured when trying to correct timestamps.\n'
        print 'Data not saved yet.\n'
        print 'Type or copy/pase this into the python console to save data with uncorrected time stamps: Save_Data(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)'
        print 'That the timestamps are uncorrected just means that they are too long by about up to (depends on timebase setup and SYNCH_MODE) several scope screen widths; this is alwyas the same amount,\
            and thus the differences between timetags are still good.'
        print 'Attempting to save data...\n'
        if int(len(SMR)) > 0:
            try:
                Save_Data(SMR, SCOPE_MEASUREMENT_HEADER)
                try:
                    IVScopeSafeExitCustomMessage("Properly closing scope and exiting script. In some cases scope may already be closed: 'InvalidSession: Invalid session handle. The resource might be closed.'")
                except:
                    if LOCK_SCOPE == "YES":
                        print 'Scope connection lost. The scope front panel is likely locked.  Use Keysight IO Libraries connection expert to unlock it with :SYSTem:LOCK 0  You may need to re-enable the scope connection and do a device clear, as well as reset the Pythion interface.'
                    else:
                        print 'Scope connection lost. Use Keysight IO Libraries connection expert to unlock it with :SYSTem:LOCK 0  You may need to re-enable the scope connection and do a device clear, as well as reset the Pythion interface.'
            except Exception as err:
                print 'Exception: ' + str(err.message) + "\n"
                print "Generic error, possibly a timeout."
                print 'Attempting to save data...\n'
                Save_Data(SMR, SCOPE_MEASUREMENT_HEADER)
        else:
            print "No data to save."
        try:
            IVScopeSafeExitCustomMessage("Properly closing scope and exiting script. In some cases scope may already be closed: 'InvalidSession: Invalid session handle. The resource might be closed.'")
        except:
            if LOCK_SCOPE == "YES":
                print 'Scope connection lost. The scope front panel is likely locked.  Use Keysight IO Libraries connection expert to unlock it with :SYSTem:LOCK 0  You may need to re-enable the scope connection and do a device clear, as well as reset the Pythion interface.'
            else:
                print 'Scope connection lost. Use Keysight IO Libraries connection expert to unlock it with :SYSTem:LOCK 0  You may need to re-enable the scope connection and do a device clear, as well as reset the Pythion interface.'

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define a Function for Saving Data  - this is only used in case of an acquisition timeout
##############################################################################################################################################################################
##############################################################################################################################################################################

def Save_Data(SMR, SMH):

    try:
        if NUMBER_ACQUISITIONS == 0:
            IVScopeSafeExitCustomMessage("No data to save. Properly closing scope and exiting script.")

        if type(SMR) == list:
            SMR = np.asarray(SMR, dtype = float)

        ##############################################################################################################################################################################
        ## Save Data

        ## Save measurement data
        if SAVE_FORMAT == "CSV" and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
            ## Actually save data in csv format - openable in Microsoft XL and most other software...
            filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Measurements.csv"
            with open(filename, 'w') as filehandle:
                if ACQ_TYPE == "AVER":
                    filehandle.write("Trigger time stamps for average acquisition mode are incorrect (too short).  Further, they mean:  How long to complete N averages.\n")
                if SYNCH_METHOD == "HIGH_SR":
                        filehandle.write("Trigger time stamps for the acquisition method used (HIGH_SR) are up to 100 ms too long, and this can vary with each acquisition.\n")
                if MATH_ON == 1:
                        filehandle.write("Trigger time stamps for when math is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with math on and off.\n")
                if ENABLE_PRECISION_MODE == "YES":
                        filehandle.write("Trigger time stamps for when precion mode is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with precision mode on and off.\n")
                filehandle.write(str(SMH))
                np.savetxt(filehandle, SMR, delimiter=',')

            del filehandle, filename

        elif SAVE_FORMAT == "NUMPY" and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
            filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Measurements.npy"
            with open(filename, 'wb') as filehandle: # wb means open for writing in binary; can overwrite
                np.save(filehandle, SMR)
            filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Measurements_Header.csv"
            with open(filename, 'w') as filehandle:
                if ACQ_TYPE == "AVER":
                    filehandle.write("Trigger time stamps for average acquisition mode are incorrect (too short).  Further, they mean:  How long to complete N averages.\n")
                if SYNCH_METHOD == "HIGH_SR":
                        filehandle.write("Trigger time stamps for the acquisition method used (HIGH_SR) are up to 100 ms too long, and this can vary with each acquisition.\n")
                if MATH_ON == 1:
                        filehandle.write("Trigger time stamps for when math is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with math on and off.\n")
                if ENABLE_PRECISION_MODE == "YES":
                        filehandle.write("Trigger time stamps for when precion mode is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with precision mode on and off.\n")
                filehandle.write(str(SMH))
                filehandle.write("This is just a header file. Data saved separately.")

        ## Save trigger time stamps
        if SAVE_TRIGGER_TIME_STAMPS_SEPARATELY == "YES":
            filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Trigger_Time_Stamps.csv"
            if USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
                with open(filename, 'w') as filehandle:
                    filehandle.write("Apparent trigger times (s)\n")
                    if ACQ_TYPE == "AVER":
                        filehandle.write("Trigger time stamps for average acquisition mode are incorrect (too short).  Further, they mean:  How long to complete N averages.\n")
                    if SYNCH_METHOD == "HIGH_SR":
                        filehandle.write("Trigger time stamps for the acquisition method used (HIGH_SR) are up to 100 ms too long, and this can vary with each acquisition.\n")
                    if MATH_ON == 1:
                        filehandle.write("Trigger time stamps for when math is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with math on and off.\n")
                    if ENABLE_PRECISION_MODE == "YES":
                        filehandle.write("Trigger time stamps for when precion mode is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with precision mode on and off.\n")
                    np.savetxt(filehandle, SMR, delimiter=',')
            elif USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
                with open(filename, 'w') as filehandle:
                    filehandle.write("Apparent trigger times (s)\n")
                    if ACQ_TYPE == "AVER":
                        filehandle.write("Trigger time stamps for average acquisition mode are incorrect (too short).  Further, they mean:  How long to complete N averages.\n")
                    if SYNCH_METHOD == "HIGH_SR":
                        filehandle.write("Trigger time stamps for the acquisition method used (HIGH_SR) are up to 100 ms too long, and this can vary with each acquisition.\n")
                    np.savetxt(filehandle, SMR[:,1], delimiter=',')
            del filename, filehandle

        sys.stdout.write("Data saved.\n\n")

    except IOError as err:
        print 'Scope connection already closed (not a scope error).'
        print 'Unable to open file: ' + str(err.strerror) + str(err.message)
        print 'Most likely the file is already opened manually.  Close it and run manually run that section of code.'
        print 'Type or copy/pase this into the python console to save: Save_Data(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)'
        sys.exit("Aborting script.")

    except Exception as err:
        print 'Scope connection already closed (not a scope error).'
        print 'Exception: ' + str(err.message) + "\n"
        sys.exit("Unable to save data, possibly due to a memory error.  Aborting script.")

    except MemoryError as err:
        print 'Scope connection already closed (not a scope error).'
        print 'Exception: MemoryError\n'

##############################################################################################################################################################################
##############################################################################################################################################################################
## Define a Function to report the statistics
##############################################################################################################################################################################
##############################################################################################################################################################################

def do_stats(SMR, SMH, SRP):
    try:
        if type(SMR) == list:
            SMR = np.asarray(SMR, dtype = float)

        NUMBER_ACQUISITIONS = np.shape(SMR)
        NUMBER_ACQUISITIONS = NUMBER_ACQUISITIONS[0]
        print str(NUMBER_ACQUISITIONS) + " total acquisitions were performed.\n"

        if (REPORT_MEASUREMENT_STATISTICS == "YES" or REPORT_THRUPUT_STATISTICS == "YES") and NUMBER_ACQUISITIONS > 1:
            DELTA_TIMES = np.zeros([NUMBER_ACQUISITIONS-1])
            if USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
                TIMES = SMR[:,1]
                for n in range (0,NUMBER_ACQUISITIONS-1,1):
                    DELTA_TIMES[n] = SMR[n+1,1] - SMR[n,1]
            elif USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
                TIMES = SMR
                for n in range (0,NUMBER_ACQUISITIONS-1,1):
                    DELTA_TIMES[n] = SMR[n+1] - SMR[n]
            del n
            LAST_TIME = TIMES[NUMBER_ACQUISITIONS-1]

        if REPORT_MEASUREMENT_STATISTICS == "YES" and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO" and NUMBER_ACQUISITIONS > 1 and NUMBER_MEASUREMENTS > 0:
            print "MEASURMENT STATISTICS:\n"

            print "Number of measurements: " + str(NUMBER_ACQUISITIONS)
            print "Total time of acquisition was " + str('%.3f' % (LAST_TIME)) + " seconds.\n"
            print "The measurments were made on a "  + str('{:,.0f}'.format(SRP [1])) + " point record."
            print "The actual sample rate was:       " + str('{:,.0f}'.format(SRP[0])) + " Sa/s"
            print "                                  " + str('{:,.0f}'.format(SRP[0]/1e9)) + " GSa/s"
            print "                                  " + str('{:,.0f}'.format(SRP[0]/1e6)) + " MSa/s"
            print "                                  " + str('{:,.0f}'.format(SRP[0]/1e3)) + " kSa/s\n"
            print "The time capture per trigger was: " + str('{:,.3e}'.format(TimeScale*10.0)) + " seconds"
            print "                                  " + str('{:,.3e}'.format(TimeScale*10.0/1.0e-3)) + " ms"
            print "                                  " + str('{:,.3e}'.format(TimeScale*10.0/1.0e-6)) + " us"
            print "                                  " + str('{:,.3e}'.format(TimeScale*10.0/1.0e-9)) + " ns"
            print "                                  " + str('{:,.3e}'.format(TimeScale*10.0/1.0e-12)) + " ps\n"
            print "This gave an effective sample rate of: " + str('{:,.0f}'.format(SRP[1]/TimeScale/10.0)) + " Sa/s"
            print "                                       " + str('{:,.0f}'.format(SRP[1]/TimeScale/10.0/1.0e9)) + " GSa/s"
            print "                                       " + str('{:,.0f}'.format(SRP[1]/TimeScale/10.0/1.0e6)) + " MSa/s"
            print "                                       " + str('{:,.0f}'.format(SRP[1]/TimeScale/10.0/1.0e3)) + " kSa/s\n"

            for n in range (0,NUMBER_MEASUREMENTS,1):
                m_avg     = np.mean(SMR[:,n+2])
                m_std_dev = np.std(SMR[:,n+2])
                m_max     = np.max(SMR[:,n+2])
                m_min     = np.min(SMR[:,n+2])
                m_range    = m_max - m_min

                print "Measurement  Statistics for " + str(list(SMH.strip('\n').split(','))[n+2]) + ":"
                print "\tAverage:                " + str('%.5e' % (m_avg))
                print "\tStandard deviation:     " + str('%.5e' % (m_std_dev))
                print "\tMinimum:                " + str('%.5e' % (m_min))
                print "\tMaximum:                " + str('%.5e' % (m_max))
                print "\tRange:                  " + str('%.5e' % (m_range)) + "\n"

                Ymax = m_max
                if Ymax > 0:
                    Ymax = Ymax*1.1
                elif Ymax < 0:
                    Ymax = Ymax*0.9
                elif Ymax == 0:
                    Ymax = 0.1

                Ymin = m_min
                if Ymin > 0:
                    Ymin = Ymin*0.9
                elif Ymin < 0:
                    Ymin = Ymin*1.1
                elif Ymin == 0:
                    Ymin = -0.1

                print str(list(SMH.strip('\n').split(','))[n+2]) + ") vs. apparent trigger time (s):"
                print "\tNOTE:  Trigger timestamps are based off of computer clock, not scope clock.\n"
                if ACQ_TYPE == "AVER":
                    print "\tNOTE: Trigger time stamps for average acquisition mode are incorrect (too short).  Further, they mean:  How long to complete N averages.\n"
                if SYNCH_METHOD == "HIGH_SR":
                    print "\tNOTE: Trigger time stamps for the acquisition method used (HIGH_SR) are up to 100 ms too long, and this can vary with each acquisition.\n"
                if MATH_ON == 1:
                    print "\tNOTE: Trigger time stamps for when math is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with math on and off.\n"
                if ENABLE_PRECISION_MODE == "YES":
                    print "\tNOTE:  Trigger time stamps for when precion mode is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with precision mode on and off.\n"
                plt.plot(TIMES,SMR[:,n+2],'r+')
                plt.ylim(Ymin,Ymax)
                plt.xlabel("Apparent Trigger Time (s)")
                plt.ylabel(str(list(SMH.strip('\n').split(','))[n+2]))
                plt.show()

                print "\n"
                print "Historgam of " +  str(list(SMH.strip('\n').split(','))[n+2]) + ":"
                plt.hist(SMR[:,n+2],bins = NUMBER_BINS)
                plt.xlabel( str(list(SMH.split(','))[n+2]))
                plt.ylabel("Hits")
                plt.show()
            del n, m_avg, m_std_dev, m_min, m_max, m_range, Ymin, Ymax

        if REPORT_THRUPUT_STATISTICS == "YES" and NUMBER_ACQUISITIONS > 2:

            thruput_avg     = np.mean(DELTA_TIMES)
            thruput_std_dev = np.std(DELTA_TIMES)
            thruput_max     = np.max(DELTA_TIMES)
            thruput_min     = np.min(DELTA_TIMES)
            thruputrange    = thruput_max - thruput_min

            print "THROUGHPUT STATISTICS:\n"
            print "\tNOTE:  Trigger timestamps are based off of computer clock, not scope clock.\n"
            if ACQ_TYPE == "AVER":
                    print "\tNOTE: Trigger time stamps for average acquisition mode are incorrect (too short).  Further, they mean:  How long to complete N averages.\n"
            if SYNCH_METHOD == "HIGH_SR":
                print "\t NOTE: Trigger time stamps for the acquisition method used (HIGH_SR) are up to 100 ms too long, and this can vary with each acquisition."
            if MATH_ON == 1:
                print "\tNOTE: Trigger time stamps for when math is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with math on and off.\n"
            if ENABLE_PRECISION_MODE == "YES":
                print "\tNOTE:  Trigger time stamps for when precion mode is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with precision mode on and off.\n"
            print "Trigger Time Differences (s):"
            print "\tAverage time betweentriggers"
            print "\t   was no more than:       " + str('%.5f' % (thruput_avg)) + " seconds (" +     str('%.2f' % (1.0/thruput_avg)) + " Hz)."
            print "\tStandard deviation:        " + str('%.5f' % (thruput_std_dev)) + " seconds (" + str('%.2f' % ((thruput_std_dev/thruput_avg)*float(10**3))) + " parts per thousand)."
            print "\tMinimum:                   " + str('%.5f' % (thruput_min)) + " seconds"
            print "\tMaximum:                   " + str('%.5f' % (thruput_max)) + " seconds"
            print "\tRange:                     " + str('%.5f' % (thruputrange)) + " seconds"
            print "\tTotal time of acquisition: " + str('%.5f' % (LAST_TIME)) + " seconds"
            print "\tNumber of triggers:        " + str('%.0f' % (NUMBER_ACQUISITIONS)) + "\n"

            indices = np.linspace(1,NUMBER_ACQUISITIONS,NUMBER_ACQUISITIONS,dtype=int)
            plt.plot(indices,TIMES,'r+')
            plt.xlim(-1,NUMBER_ACQUISITIONS+1)
            plt.xlabel("Acquisition Number")
            plt.ylabel("Apparent Trigger Time (s)")
            plt.show()

            print "\n"
            indices = np.linspace(1,NUMBER_ACQUISITIONS-1,NUMBER_ACQUISITIONS-1,dtype=int)
            plt.plot(indices,DELTA_TIMES,'r+')
            plt.xlabel("Acquisition Number-1")
            plt.ylabel("Delta Trigger Times (s)")
            plt.show()

            print "\n"
            plt.hist(DELTA_TIMES,bins = NUMBER_BINS)
            plt.xlabel("Trigger Time Differences (s)")
            plt.ylabel("Hits")
            plt.show()

            del thruput_avg, thruput_std_dev, thruput_max, thruput_min, thruputrange, indices

        ## Re-Issue some warnings
        if ACQ_TYPE == "AVER":
            print "WARNING! Trigger time stamps for average acquisition mode are incorrect (too short).  Further, they mean:  How long to complete N averages.\n"
        if SYNCH_METHOD == "HIGH_SR":
            print "WARNING! Trigger time stamps for the acquisition method used (HIGH_SR) are up to 100 ms too long, and this can vary with each acquisition\n."
        if MATH_ON == 1:
            print "WARNING! Trigger time stamps for when math is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with math on and off.\n"
        if ENABLE_PRECISION_MODE == "YES":
            print "WARNING! Trigger time stamps for when precion mode is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with precision mode on and off.\n"

    except Exception as err:
        print 'Exception: ' + str(err.message) + "\n"
        print 'Exception occurred in Statistics and Throughput reporting section. Scope already closed (not a scope error).\n'
        print 'Data should/could already be saved...'
        sys.exit("Exiting script.")

##############################################################################################################################################################################
##############################################################################################################################################################################
## Do some basic checks
##############################################################################################################################################################################
##############################################################################################################################################################################

try:
    if GLOBAL_TOUT < 10000:
        print "Global time out (GLOBAL_TOUT) less than 10,000 milliseconds.  Setting it to 10,000 ms."
        GLOBAL_TOUT = 10000

    if RUN_CONTROL_BY_TIME_OR_NUMBER == "TIME" and TIME_TO_RUN < 1:
        TIME_TO_RUN = 10
        sys.stdout.write("Setting TIME_TO_RUN to 10 seconds.\n\n")

    if RUN_CONTROL_BY_TIME_OR_NUMBER == "NUMBER" and type(NUMBER_ACQUISITIONS) != int:
        sys.exit("NUMBER_ACQUISITIONS must be an integer and greater than 0.  Scope connection not made yet. Exiting script.")

    if RUN_CONTROL_BY_TIME_OR_NUMBER == "NUMBER" and NUMBER_ACQUISITIONS <= 0:
        sys.exit("NUMBER_ACQUISITIONS must be an integer and greater than 0.  Scope connection not made yet. Exiting script.")

    if MEAS_METHOD != "SCRIPT" and MEAS_METHOD != "SCOPE":
        sys.exit("MEAS_METHOD not defined properly.  Scope connection not made yet. Exiting script.")

    if SCOPE_SETUP_METHOD != "SCRIPT" and SCOPE_SETUP_METHOD != "AS_IS":
        sys.exit("SCOPE_SETUP_METHOD not defined properly.  Scope connection not made yet. Exiting script.")

    if ACQUISITION_TIMEOUT_BEHAVIOR != "SAVE_AND_ABORT" and ACQUISITION_TIMEOUT_BEHAVIOR != "TRY_AGAIN":
        sys.exit("ACQUISITION_TIMEOUT_BEHAVIOR not defined properly.  Scope connection not made yet. Exiting script.")

    if SYNCH_METHOD != "FAST" and SYNCH_METHOD != "HIGH_SR":
        sys.exit("SYNCH_METHOD not defined properly.  Scope connection not made yet. Exiting script.")

    if ENABLE_PRECISION_MODE != "YES" and ENABLE_PRECISION_MODE != "NO":
        sys.exit("ENABLE_PRECISION_MODE not defined properly.  Scope connection not made yet. Exiting script.")

    if SAVE_FORMAT != "NUMPY" and SAVE_FORMAT != "CSV":
        sys.exit("SAVE_FORMAT not properly defined.  Scope connection not made yet. Exiting script before collecting data...")

    if USE_AS_TRIGGER_TIME_RECORDER_ONLY != "YES" and USE_AS_TRIGGER_TIME_RECORDER_ONLY != "NO":
        sys.exit("USE_AS_TRIGGER_TIME_RECORDER_ONLY not properly defined.  Scope connection not made yet. Exiting script before collecting data...")

    if RUN_CONTROL_BY_TIME_OR_NUMBER != "TIME" and RUN_CONTROL_BY_TIME_OR_NUMBER != "NUMBER":
        sys.exit("RUN_CONTROL_BY_TIME_OR_NUMBER not properly defined.  Scope connection not made yet. Exiting script before collecting data...")

    if GET_SCREENSHOT != "EVERY" and GET_SCREENSHOT != "NO" and GET_SCREENSHOT != "FIRST" and GET_SCREENSHOT != "LAST" and GET_SCREENSHOT != "FIRSTANDLAST":
        sys.exit("GET_SCREENSHOT not properly defined.  Scope connection not made yet. Exiting script before collecting data...")

    if GET_SCREENSHOT != "NO":
        if INVERT_BACKGROUND != "YES" and INVERT_BACKGROUND != "NO":
            sys.exit("INVERT_BACKGROUND not properly defined.  Scope connection not made yet. Exiting script before collecting data...")

    if NUMBER_BINS != "DEFAULT" and type(NUMBER_BINS) != int:
        sys.exit('NUMBER_BINS not properly defined.  It must be "DEFAULT" or an integer (e.g. 1 or 2, not 1.0..., and no quotes). Scope connection not made yet. Exiting script before collecting data...')

    if (NUMBER_BINS != "DEFAULT" and NUMBER_BINS < 10) or NUMBER_BINS == "DEFAULT":
        NUMBER_BINS = 10

except Exception as err:
    print 'Exception: ' + str(err.message) + "\n"
    print 'One of the initialization constants is not defined or has been re-named. \n'
    sys.exit("Exiting script. Connection to scope not yet made... ")

##############################################################################################################################################################################
##############################################################################################################################################################################
## End Function definitions, Begin Main Script
##############################################################################################################################################################################
##############################################################################################################################################################################

##############################################################################################################################################################################
##############################################################################################################################################################################
## Begin all setup
##############################################################################################################################################################################
##############################################################################################################################################################################

try:

    ##############################################################################################################################################################################
    ##############################################################################################################################################################################
    ## Connect and initialize scope


    ## Define VISA Resource Manager & Install directory
    ## This directory will need to be changed if VISA was installed somewhere else.
    rm = visa.ResourceManager('C:\\Windows\\System32\\visa32.dll') # this uses pyvisa
    ## This is more or less ok too: rm = visa.ResourceManager('C:\\Program Files (x86)\\IVI Foundation\\VISA\\WinNT\\agvisa\\agbin\\visa32.dll')
    ## In fact, it is generally not needed to call it explicitly
    ## rm = visa.ResourceManager()

    ## Open Connection(s)
    ## Define & open the scope by the VISA address ; # this uses pyvisa
    try:
        KsInfiniiVisionX = rm.open_resource(SCOPE_VISA_ADDRESS)
    except Exception as err:
        print 'Exception: ' + str(err.message) + "\n"
        print "Unable to connect to oscillopscope at " + str(SCOPE_VISA_ADDRESS) + ". Aborting script.\n"
        sys.exit()

    ## Set Global Timeout
    ## This can be used wherever, but local time outs are used for Arming, Triggering, and Finishing the acquisition... Thus it mostly handles IO time outs
    KsInfiniiVisionX.timeout = GLOBAL_TOUT

    ## Clear the instrument bus
    KsInfiniiVisionX.clear()

    ## Clear all registers and errors
    KsInfiniiVisionX.query("*CLS;*OPC?")

    ## End connect and initialize scope
    ##############################################################################################################################################################################

    ##############################################################################################################################################################################
    ## Get and parse IDN string
    IDN = str(KsInfiniiVisionX.query("*IDN?"))
    ## Parse IDN
    IDN = IDN.split(',') # IDN parts are separated by commas, so parse on the commas
    ##mfg = IDN[0]
    MODEL = IDN[1]
    ##SN = IDN[2]
    FW = IDN[3]
    LIC =  str(KsInfiniiVisionX.query("*OPT?"))

    if MODEL[3] == "-":
        GENERATION = "IVX"
        FAMILY = int(MODEL[6])
        if FAMILY == 3:
            FAMILY = str(FAMILY) + str(MODEL[10])
    else:
        GENERATION = "IVnotX"
        FAMILY = int(MODEL[3])

    ## Check the firmware
    FW = FW[0:5]
    FW_TOO_OLD = 0
    if GENERATION == "IVX":
         MODEL = MODEL.replace("-","")
         MODEL = MODEL.replace(" ","")
         if FAMILY == 2 or FAMILY == "3A":
             if FW < 2.41:
                 FW_TOO_OLD = 1
         elif FAMILY == "3T" or FAMILY == 4:
             if FW < 4.06:
                 FW_TOO_OLD = 1
         elif FAMILY == 6:
             if FW < 6.11:
                 FW_TOO_OLD = 1
    else:
          if FW < 6.16:
              FW_TOO_OLD = 1

    if FW_TOO_OLD == 1:
        IVScopeSafeExitCustomMessage("The scope's firmware is too old.  Please go to the following link to update the firmware: http://www.keysight.com/support/" + str(MODEL) + " , then to the Drivers, Software, and Firmware tab, and choose: Installing InfiniiVision xxx Series Firmware. Properly closing scope and exiting script.\n")

    NUMBER_ANALOG_CHS = int(MODEL[len(MODEL)-2])

    if MODEL[0] == "M":
        SCOPE_TYPE = "MSO"
    else:
        if FAMILY == 5:
            SCOPE_TYPE = "DSO"
        else: # Checking for MSO Upgrade
           if "MSO" in LIC:
              SCOPE_TYPE = "MSO"
           else:
               SCOPE_TYPE = "DSO"

    if "LSS" in LIC or "AMS" in LIC or "CAN" in LIC or "232" in LIC or "FRC" in LIC or "SND" in LIC or "FLX" in LIC \
        or "533" in LIC or "EMBD" in LIC or "AUTO" in LIC or "FLEX" in LIC or "COMP" in LIC or "AUDIO" in LIC \
        or "AERO" in LIC or "SENSOR" in LIC or "CANFD" in LIC or "USBFL" in LIC or "USBH" in LIC:
            SERIAL_LICENSED = 1
    else:
        SERIAL_LICENSED = 0

    if GENERATION == "IVX" and FAMILY == 6:
        if "JITTER" in LIC:
            JITTER_LICENSED = 1
        else:
            JITTER_LICENSED = 0

    if "MASK" in LIC or "MST" in LIC:
       MTEST_LICENSED = 1
    else:
        MTEST_LICENSED = 0

    ## End get and parse IDN string
    ##############################################################################################################################################################################

    ##############################################################################################################################################################################
    ##############################################################################################################################################################################
    ## Main Scope Setup
    ##############################################################################################################################################################################
    ##############################################################################################################################################################################

    if LOCK_SCOPE == "YES":
        KsInfiniiVisionX.write(":SYSTem:LOCK 1")
    elif LOCK_SCOPE == "NO":
        KsInfiniiVisionX.write(":SYSTem:LOCK 0")
    else:
        IVScopeSafeExitCustomMessage("LOCK_SCOPE not defined properly.  Properly closing scope and exiting script.")

    KsInfiniiVisionX.write(":STOP")
    KsInfiniiVisionX.write(":TRIGger:SWEep " + str(TRIGGER_SWEEP))

    if SCOPE_SETUP_METHOD == "SCRIPT":
        Scope_Setup_by_Script()
        ## User should modify the setup INSIDE this function.  Search for (Ctrl f) ##SCOPE_SETUP_BY_SCRIPT
    ## else:
        ## The scope is already setup as the user desires, for SCOPE_SETUP_METHOD = "AS_IS"

    ## Set trigger holdoff
    if SCOPE_TRIGGER_HOLDOFF == "MIN":
        if GENERATION == "IVX":
            KsInfiniiVisionX.write(":TRIGger:HOLDoff 40e-9") # Set minimum holdoff
        elif GENERATION == "IVnotX":
            KsInfiniiVisionX.write(":TRIGger:HOLDoff 60e-9") # Set minimum holdoff
    elif type(SCOPE_TRIGGER_HOLDOFF) == float or type(SCOPE_TRIGGER_HOLDOFF) == int:
        KsInfiniiVisionX.write(":TRIGger:HOLDoff " + str(SCOPE_TRIGGER_HOLDOFF))
    else:
        IVScopeSafeExitCustomMessage("SCOPE_TRIGGER_HOLDOFF not defined properly.  Properly closing scope and exiting script.")
    HO = KsInfiniiVisionX.query(":TRIGger:HOLDoff?")

    ## End Main Scope Setup
    ##############################################################################################################################################################################

    ##############################################################################################################################################################################
    ## Calculate acquisition timeout by short, overestimate method

    tRange    = float(KsInfiniiVisionX.query(":TIMebase:RANGe?"))
    tPosition = float(KsInfiniiVisionX.query(":TIMebase:POSition?"))
    SCOPE_ACQUISITION_TIME_OUT  = (tRange*2.0*10.0  + abs(tPosition)*2.0 + float(TIME_TO_TRIGGER)*1.1 + float(HO)*1.1)*1000.0 # Recall that pyvisa timeouts are in ms, so multiply by 1000

    if RUN_CONTROL_BY_TIME_OR_NUMBER == "TIME" and TIME_TO_RUN < (SCOPE_ACQUISITION_TIME_OUT/1000.0/1.1-TIME_TO_TRIGGER):
        IVScopeSafeExitCustomMessage("TIME_TO_RUN too short for scope timebase.  Increase TIME_TO_RUN or adjust scope timebase.  Properly closing scope and exiting script.")

    if SCOPE_ACQUISITION_TIME_OUT < 10000: # ms
        sys.stdout.write("Calculated Acquisition time out is very short, setting to 10 seconds minimum.\n\n")
        SCOPE_ACQUISITION_TIME_OUT = 10000

    ## End calculate acquisition timeout by short, overestimate method
    ##############################################################################################################################################################################

    ##############################################################################################################################################################################
    ##############################################################################################################################################################################
    ## Do some checks and adjustments

    ## Check for and disable mask test mode
    if MTEST_LICENSED == 1:
        MTE = int(KsInfiniiVisionX.query(":MTESt:ENABle?"))
        if MTE == 1:
            KsInfiniiVisionX.query(":MTESt:ENABle 0")
            sys.stdout.write("Mask testing not supported.  Disabling mask test. Continuing.\n\n")
            del MTE

    ## Chcek for and abort on roll and XY modes
    TIME_MODE = str(KsInfiniiVisionX.query(":TIMebase:MODE?").strip('\n'))
    if TIME_MODE == "XY" or TIME_MODE == "ROLL":
        IVScopeSafeExitCustomMessage("XY and Roll modes not supported in this script.  Properly closing scope and exiting script.")

    ## If X6000A, check for eye mode and color grade mode and disable, check for jitter mode and switch to SYNCH_METHOD = "FAST"
    if GENERATION == "IVX" and FAMILY == 6:
        if JITTER_LICENSED == 1:
            RTS = int(KsInfiniiVisionX.query(":RTEYe:STATe?"))
            if RTS == 1:
                KsInfiniiVisionX.query(":RTEYe:STATe 0")
                sys.stdout.write("Eye mode not supported.  Disabling eye mode. Continuing.\n\n")
            JTS = int(KsInfiniiVisionX.query(":JITTer:STATe?"))
            if JTS == 1:
                SYNCH_METHOD = "FAST"
                sys.stdout.write('Setting SYNCH_METHOD to "FAST" for Jitter mode.\n\n')
            del RTS, JTS
        CGS = int(KsInfiniiVisionX.query(":CGRade:STATe?"))
        if CGS == 1:
            KsInfiniiVisionX.query(":CGRade:STATe 0")
            sys.stdout.write("Color grading not supported.  Disabling color grade. Continuing.\n\n")
        del CGS

    ## Detect if Math is on, and if so, set SYNCH_METHOD to "FAST", unless USE_AS_TRIGGER_TIME_RECORDER_ONLY = "YES",
        ## in which case, disable math
    FFT_ON = 0
    if GENERATION == "IVnotX":
        MATH_ON = int(KsInfiniiVisionX.query(":FUNCtion:DISPlay?"))
        if MATH_ON == 1 and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
            KsInfiniiVisionX.query(":FUNCtion:DISPlay 0")
            MATH_ON = 0
    elif GENERATION == "IVX":
        if FAMILY == 2 or FAMILY == "3A":
            MATH_ON = int(KsInfiniiVisionX.query(":FUNCtion:DISPlay?"))
            if MATH_ON == 1 and SYNCH_METHOD == "FAST":
                KsInfiniiVisionX.query(":FUNCtion:DISPlay 0")
                MATH_ON = 0
        elif FAMILY == 4:
            for ch in range (1,5,1):
                MATH_ON = int(KsInfiniiVisionX.query(":FUNCtion" + str(ch) + ":DISPlay?"))
                if MATH_ON == 1 and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
                    KsInfiniiVisionX.write(":FUNCtion" + str(ch) + ":DISPlay 0")
                    MATH_ON = 0
                    break
            del ch
        elif FAMILY == "3T":
            FFT_ON = int(KsInfiniiVisionX.query(":FFT:DISPlay?"))
            if FFT_ON == 1 and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
                KsInfiniiVisionX.write(":FFT:DISPlay 0")
                FFT_ON = 0
            for ch in range (1,3,1):
                MATH_ON = int(KsInfiniiVisionX.query(":FUNCtion" + str(ch) + ":DISPlay?"))
                if MATH_ON == 1 and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
                    KsInfiniiVisionX.write(":FUNCtion" + str(ch) + ":DISPlay 0")
            del ch
        elif FAMILY == 6:
            for ch in range (1,5,1):
                MATH_ON = int(KsInfiniiVisionX.query(":FUNCtion" + str(ch) + ":DISPlay?"))
                if MATH_ON == 1 and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
                    KsInfiniiVisionX.write(":FUNCtion" + str(ch) + ":DISPlay 0")
                    MATH_ON = 0
                elif MATH_ON == 1 and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
                    break
            del ch
    if (MATH_ON == 1 or FFT_ON == 1) and SYNCH_METHOD != "FAST":
        SYNCH_METHOD = "FAST"
        sys.stdout.write('Setting SYNCH_METHOD to "FAST" becasue math is enabled.\n\n')
    del FFT_ON

    if USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
        SYNCH_METHOD = "FAST"
        GET_SCREENSHOT = "NO"
        KsInfiniiVisionX.write(":TRIGger:SWEep NORMal")
        KsInfiniiVisionX.write(":ACQuire:TYPE NORMal")
        KsInfiniiVisionX.write(":TIMebase:SCALe 5e-9")
        KsInfiniiVisionX.write(":TIMebase:POSition 0")
        KsInfiniiVisionX.write(":TIMebase:MODE MAIN")
        KsInfiniiVisionX.write(":MEASure:CLEar")
        KsInfiniiVisionX.write(":MARKer:MODE OFF")
        if SERIAL_LICENSED == 1:
            if GENERATION == "IVX" and FAMILY != 2:
                KsInfiniiVisionX.write(":SBUS1:DISPlay 0")
                KsInfiniiVisionX.write(":SBUS2:DISPlay 0")
            else:
                KsInfiniiVisionX.write(":SBUS:DISPlay 0")
        if GENERATION == "IVX" and FAMILY == 6:
            KsInfiniiVisionX.write(":ACQuire:MODE MRTime")

    ## Disable displayed scope measurements if:
    if MEAS_METHOD == "SCRIPT" or USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
        KsInfiniiVisionX.write(":MEASure:SCRatch")

    ## Check :ACQuire:TYPE
    ACQ_TYPE  = str(KsInfiniiVisionX.query(":ACQuire:TYPE?").strip('\n'))
    if ACQ_TYPE == "AVER" or ACQ_TYPE == "AVERage":
        ACQ_TYPE = "AVER"
        SYNCH_METHOD = "FAST"
        sys.stdout.write('Setting SYNCH_METHOD to "FAST" becasue average acquisition mode is enabled.\n\n')
        ## SYNCH_METHOD = "HIGH_SR" uses the :SINGle command, which does not work for average acquisition mode
        NUMBER_AVGS = int(KsInfiniiVisionX.query(":ACQuire:COUNt?").strip('\n'))
        if NUMBER_AVGS == 1:
            ACQ_TYPE = "HRESolution" # Average mode with number averages actually means high res mode.
            KsInfiniiVisionX.write(":ACQuire:TYPE HRESolution")
        else:
            SCOPE_ACQUISITION_TIME_OUT = SCOPE_ACQUISITION_TIME_OUT*float(NUMBER_AVGS)
    elif ACQ_TYPE == "HRes" or ACQ_TYPE == "HRESolution":
        ACQ_TYPE = "HRes"

    ## Check for and abort on eqialvalent time mode or segemtned memory
    ACQ_MODE = str(KsInfiniiVisionX.query(":ACQuire:MODE?").strip('\n'))
    if ACQ_MODE == "ETIMe" or ACQ_MODE == "ETIM":
        ACQ_MODE = "ETIM"
    if ACQ_MODE == "ETIM" and ACQ_TYPE != "AVER" and GENERATION == "InotVX":
        IVScopeSafeExitCustomMessage("Equivalent time mode not supported in this script.  Properly closing scope and exiting script.  Use alternate script.")
        ## Interestingly, the older 5/6/7000s, if in avergage mode (type, see below), report that the mode is etime, and not real time.  That's OK for this check... mostly...
    elif ACQ_MODE == "SEGMented" or ACQ_MODE == "SEGM":
        IVScopeSafeExitCustomMessage("Segmented memory not supported in this script.  Properly closing scope and exiting script.  Use alternate script.")
    elif ACQ_MODE == "ETIM" and GENERATION == "IVX":
        IVScopeSafeExitCustomMessage("Equivalent time mode not supported in this script.  Properly closing scope and exiting script.  Use alternate script.")
    ## Ensure that only the current value of the measurements are returned if MEAS_METHOD = "SCOPE" ; X2000A does not support statistics
    if FAMILY != 2 and MEAS_METHOD == "SCOPE":
        KsInfiniiVisionX.write(":MEASure:STATistics CURRent")

    ## Find number of measurements on and pre-allocate Scope_Measurement_Results array
    if MEAS_METHOD == "SCRIPT" and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
        NUMBER_MEASUREMENTS = len(MEASURE_LIST)
    elif MEAS_METHOD == "SCOPE" and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
        NUMBER_MEASUREMENTS = len(KsInfiniiVisionX.query(":MEASure:RESults?").split(','))/2
    else:
        NUMBER_MEASUREMENTS = 0
    if NUMBER_MEASUREMENTS == 0 and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO" and GET_SCREENSHOT == "NO":
        IVScopeSafeExitCustomMessage("No measurements defined or enabled and no screenshots enabled.  Properly closing scope and exiting script.")
    else:
      Scope_Measurement_Results = []

    del TIME_MODE, ACQ_MODE

    ## Enable/disable Precion Mode
    if ENABLE_PRECISION_MODE == "YES" and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO" and ACQ_TYPE != "AVER" and ACQ_TYPE != "HRes":
        if GENERATION == "IVnotX":
            KsInfiniiVisionX.write(":SYSTem:PRECision ON")
        if GENERATION == "IVX" and FAMILY == 6:
            KsInfiniiVisionX.write(":SYSTem:PRECision ON")
            KsInfiniiVisionX.write(":SYSTem:PRECision:LENGth " + str(PRECISION_LENTGH_X6000A_ONLY))
    elif ENABLE_PRECISION_MODE == "NO" or USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES" or ACQ_TYPE == "AVER" or ACQ_TYPE == "HRES":
        if GENERATION == "IVX" and FAMILY == 6:
            KsInfiniiVisionX.write(":SYSTem:PRECision OFF")
            ENABLE_PRECISION_MODE = "NO"
        elif GENERATION == "IVnotX":
            KsInfiniiVisionX.write(":SYSTem:PRECision OFF")
            ENABLE_PRECISION_MODE = "NO"

    if GENERATION == "IVX" and FAMILY == 6 and SYNCH_METHOD == "HIGH_SR":
            KsInfiniiVisionX.write(":ACQuire:MODE RTIMe")

    ## Always save time stamps for USE_AS_TRIGGER_TIME_RECORDER_ONLY = "YES"
    if USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
        SAVE_TRIGGER_TIME_STAMPS_SEPARATELY = "YES"

    ## Issue some warnings
    if ACQ_TYPE == "AVER":
        sys.stdout.write("WARNING! Trigger time stamps for average acquisition mode are incorrect (too short).  Further, they mean:  How long to complete N averages.\n\n")
    if SYNCH_METHOD == "HIGH_SR":
        sys.stdout.write("WARNING! Trigger time stamps for the acquisition method used (HIGH_SR) are up to 100 ms too long, and this can vary with each acquisition.\n\n")
    if MATH_ON == 1:
        sys.stdout.write("WARNING! Trigger time stamps for when math is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with math on and off.\n\n")
    if ENABLE_PRECISION_MODE == "YES":
        sys.stdout.write("WARNING! Trigger time stamps for when precion mode is on are not really valid because the math takes extra time to synchronize. They will be somewhat too long. Consider characterizing the throughput with precision mode on and off.\n\n")

    ## End checks and adjustments
    ##############################################################################################################################################################################
    ##############################################################################################################################################################################

    ##############################################################################################################################################################################
    ## Check that user defined measurements are basically OK - the results may not make sense, but the measurements are properly defined.

    ## Get timebase info (needed later too)
    TimeScale = float(KsInfiniiVisionX.query(":TIMebase:SCALe?"))
    TimePosition = float(KsInfiniiVisionX.query(":TIMebase:POSition?"))
    TimeReference = str(KsInfiniiVisionX.query(":TIMebase:REFerence?")).strip("\n")
    if TimeReference == ("CENT" or "CENTer"):
        TimeReference = "CENTer"
    elif TimeReference == ("RIGH" or "RIGHt"):
        TimeReference = "RIGHt"

    ## Do a fake run at a short time base (so it's quick) and check that there are no errors generated by the measurements, then reset the timebase...
    if USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO" and MEAS_METHOD == "SCRIPT" and NUMBER_MEASUREMENTS > 0:

        ## But first, check to see which channels are already on
        ACH_LIST_BEFORE = np.zeros([NUMBER_ANALOG_CHS])
        if SCOPE_TYPE == "MSO":
            if FAMILY == 2:
                NUMBER_DIGITAL_CHS = 8
                DCH_LIST_BEFORE = np.zeros([NUMBER_DIGITAL_CHS])
            else:
                NUMBER_DIGITAL_CHS = 16
                DCH_LIST_BEFORE = np.zeros([NUMBER_DIGITAL_CHS])
        else:
            NUMBER_DIGITAL_CHS = 0 # Scope is DSO
        for ch in range (1,NUMBER_ANALOG_CHS+1,1):
            ACH_LIST_BEFORE[ch-1] = int(KsInfiniiVisionX.query(":CHANnel" + str(ch) + ":DISPlay?"))
        if SCOPE_TYPE == "MSO":
            for d in range (0,NUMBER_DIGITAL_CHS,1):
                DCH_LIST_BEFORE[d] = int(KsInfiniiVisionX.query(":DIGital" + str(d) + ":DISPlay?"))

        KsInfiniiVisionX.write(":TIMebase:SCALe 5e-9")
        KsInfiniiVisionX.write(":TIMebase:POSition 0")
        KsInfiniiVisionX.query(":TRIGger:SWEep AUTO;*OPC?")

        KsInfiniiVisionX.write(":SINGle")
        time.sleep(.1)

        ## Do measurements.  It does not matter if they are right, but that they are well defined and don't cause scope errors
        ## This won't catch an error that for example, turns on an unintended channel or has a nonsensical result.
        KsInfiniiVisionX.write("*CLS")
        try:
            for m in range (1,NUMBER_MEASUREMENTS+1,1):
                if "WIND" in str.upper(MEASURE_LIST[m-1]) or "WINDOW" in str.upper(MEASURE_LIST[m-1]) or "GATE" in str.upper(MEASURE_LIST[m-1]):
                    sys.stdout.write("Unable to test measurement M" + str(m) + " as it uses a WINDow or cursors.  Doing so here could take a long time.  Suggest to manually check the measurement in Keysight Connection Expert.\n\n")
                else:
                    KsInfiniiVisionX.query(str(MEASURE_LIST[m-1]))
                    ## Do error check
                    Meas_Err = ErrCheck()
                    if len(Meas_Err) == 0:
                        sys.stdout.write("Measurement M" + str(m) + " is defined correctly.\n")
                        del Meas_Err
                    else:
                        IVScopeSafeExitCustomMessage("Measurement M" + str(m) + " has errors.  Properly closing scope and exiting script.\n")
        except Exception:
            print "Measurement M" + str(m) + " has errors.  Properly closing scope and exiting script.\n"
            KsInfiniiVisionX.clear()
            KsInfiniiVisionX.write(":SYSTem:LOCK 0")
            KsInfiniiVisionX.write(":STOP")
            KsInfiniiVisionX.close()
            sys.exit("Exiting script.")
        sys.stdout.write("\n")
        sys.stdout.write("While the measurements are correctly defined, they may not actually make senses.  It is up to the user to validate the results.\n\n")

        ## Reset time base
        Scope_Timebase_Reset(TimeReference, TimeScale, TimePosition)

        ## Reset trigger sweep type
        KsInfiniiVisionX.write(":TRIGger:SWEep " + str(TRIGGER_SWEEP))

        ## Now check to see which channels are on
        ACH_LIST_AFTER = np.zeros([NUMBER_ANALOG_CHS])
        if SCOPE_TYPE == "MSO":
            if FAMILY == 2:
                DCH_LIST_AFTER = np.zeros([NUMBER_DIGITAL_CHS])
            else:
                DCH_LIST_AFTER = np.zeros([NUMBER_DIGITAL_CHS])
        for ch in range (1,NUMBER_ANALOG_CHS+1,1):
            ACH_LIST_AFTER[ch-1] = int(KsInfiniiVisionX.query(":CHANnel" + str(ch) + ":DISPlay?"))
        if SCOPE_TYPE == "MSO":
            for d in range (0,NUMBER_DIGITAL_CHS,1):
                DCH_LIST_AFTER[d] = int(KsInfiniiVisionX.query(":DIGital" + str(d) + ":DISPlay?"))
            del d
        del ch

        ABORT = 0
        if np.array_equal(ACH_LIST_AFTER,ACH_LIST_BEFORE) == False:
            test = ACH_LIST_AFTER - ACH_LIST_BEFORE
            ch = 1
            for i in test:
                if i != 0:
                    ABORT = 1
                    print "One of the user defined measurements in this script turned on analog channel #" + str(ch) + ", which was previously off.  This indicates that bad data is likely to be captured.  Aborting script.\n"
                ch += 1
            del ch, i, test
        
        if SCOPE_TYPE == "MSO":
            if np.array_equal(DCH_LIST_AFTER,DCH_LIST_BEFORE) == False:
                test = DCH_LIST_AFTER - DCH_LIST_BEFORE
                for i in test:
                    if i != 0:
                        ABORT = 1
                        print "One of the user defined measurements in this script turned on digital channel #" + str(int(i)) + ", which was previously off.  This indicates that bad data is likely to be captured.  Aborting script.\n"
                del i, test

        if ABORT == 1:
            IVScopeSafeExitCustomMessage("Properly closing scope and exiting script per above message(s).  User should check measurement sources in script and which channels are on/off.  Adjust as needed.")

        del ABORT, ACH_LIST_AFTER, ACH_LIST_BEFORE
        if SCOPE_TYPE == "MSO":
            DCH_LIST_AFTER, DCH_LIST_BEFORE

    ## End check that user defined measurements are basically OK
    ##############################################################################################################################################################################

    ##############################################################################################################################################################################
    ## Create measurement header
    if MEAS_METHOD == "SCOPE" and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
        SCOPE_MEASUREMENT_HEADER = ""
        data = list(KsInfiniiVisionX.query(":MEASure:RESults?").split(','))
        for m in range (1,NUMBER_MEASUREMENTS+1,1):
            SCOPE_MEASUREMENT_HEADER =  SCOPE_MEASUREMENT_HEADER + str(data[((m-1)*2)])
            if m != NUMBER_MEASUREMENTS:
                SCOPE_MEASUREMENT_HEADER = SCOPE_MEASUREMENT_HEADER + str(',')
            elif m == NUMBER_MEASUREMENTS:
                SCOPE_MEASUREMENT_HEADER = SCOPE_MEASUREMENT_HEADER
        del data
    elif MEAS_METHOD == "SCRIPT" and USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
            SCOPE_MEASUREMENT_HEADER = SCOPE_MEASUREMENT_HEADER.strip('\n')
            SCOPE_MEASUREMENT_HEADER = "Index,Time Stamp (s)," + SCOPE_MEASUREMENT_HEADER + "\n"

    ## Create measurement header for MEAS_METHOD == "SCOPE"
    ##############################################################################################################################################################################

    ##############################################################################################################################################################################
    ## Create string of the user defined measurements to repeatedly query the scope with
    if MEAS_METHOD == "SCRIPT" and NUMBER_MEASUREMENTS > 0:
        MEAS_STRING = ""
        for m in range (1,NUMBER_MEASUREMENTS+1,1):
            if m < NUMBER_MEASUREMENTS:
                MEAS_STRING = MEAS_STRING + str(MEASURE_LIST[m-1]) + ";"
            else:
                MEAS_STRING = MEAS_STRING + str(MEASURE_LIST[m-1])

    ## End Create string of the user defined measurements to repeatedly query the scope with
    ##############################################################################################################################################################################

    ##############################################################################################################################################################################
    ##############################################################################################################################################################################
    ## End all setup
    ##############################################################################################################################################################################
    ##############################################################################################################################################################################

except Exception as err:
    print 'Exception: ' + str(err.message) + "\n"
    print "Generic error, possibly a timeout."
    IVScopeSafeExitCustomMessage("Properly closing scope and exiting script. In some cases scope may already be closed: 'InvalidSession: Invalid session handle. The resource might be closed.'")

##############################################################################################################################################################################
##############################################################################################################################################################################
## Acquire and Measure Loop
##############################################################################################################################################################################
##############################################################################################################################################################################

sys.stdout.write("Setup done.  Beginning acquisition cycle.\n\n")

try:

    if SYNCH_METHOD == "FAST":
        KsInfiniiVisionX.timeout = SCOPE_ACQUISITION_TIME_OUT

    if RUN_CONTROL_BY_TIME_OR_NUMBER == "NUMBER":
        if USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
            Start_time = time.clock()
            for n in range (1,NUMBER_ACQUISITIONS+1,1):
                if SYNCH_METHOD == "FAST":
                    delta_time = method1(SCOPE_ACQUISITION_TIME_OUT, Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)- Start_time
                elif SYNCH_METHOD == "HIGH_SR":
                    delta_time = method2(SCOPE_ACQUISITION_TIME_OUT, Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)- Start_time
                Run = [n, delta_time]
                Result = []
                if MEAS_METHOD == "SCRIPT" and NUMBER_MEASUREMENTS > 0:
                    data = (KsInfiniiVisionX.query(str(MEAS_STRING)).split(';'))
                    Scope_Measurement_Results.append(Run + data)
                elif MEAS_METHOD == "SCOPE" and NUMBER_MEASUREMENTS > 0:
                    data = list(KsInfiniiVisionX.query(":MEASure:RESults?").split(','))
                    for m in range (1,NUMBER_MEASUREMENTS+1,1):
                        Result.append(float(data[((m-1)*2)+1]))
                    Scope_Measurement_Results.append(Run + Result)
                else:
                    Scope_Measurement_Results.append(Run)
                if PAUSE_BETWEEN_ACQUISISTIONS == "YES":
                    time.sleep(TIME_TO_PAUSE)

                if GET_SCREENSHOT == "EVERY":
                    Get_Screen(GENERATION,n)
                elif (GET_SCREENSHOT == "FIRST" or GET_SCREENSHOT == "FIRSTANDLAST") and n == 1:
                    Get_Screen(GENERATION,n)
                elif  (GET_SCREENSHOT == "LAST" or GET_SCREENSHOT == "FIRSTANDLAST") and n == NUMBER_ACQUISITIONS+1:
                    Get_Screen(GENERATION,n)

            if int(len(Scope_Measurement_Results)) > 0 and NUMBER_MEASUREMENTS > 0:
                del m, delta_time, Start_time, Result, Run, data
            else:
                del delta_time, Start_time, Result, Run

        elif USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
            Start_time = time.clock()
            for n in range (1,NUMBER_ACQUISITIONS+1,1):
               RunResult = method1(SCOPE_ACQUISITION_TIME_OUT, Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)- Start_time
               Scope_Measurement_Results.append(RunResult)
               if PAUSE_BETWEEN_ACQUISISTIONS == "YES":
                   time.sleep(TIME_TO_PAUSE)
            del Start_time, RunResult

    elif RUN_CONTROL_BY_TIME_OR_NUMBER == "TIME":
        if USE_AS_TRIGGER_TIME_RECORDER_ONLY == "NO":
            NUMBER_ACQUISITIONS = 0
            Start_time = time.clock()
            while (time.clock() - Start_time) < TIME_TO_RUN:
                if SYNCH_METHOD == "FAST":
                    delta_time = method1(SCOPE_ACQUISITION_TIME_OUT, Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)- Start_time
                elif SYNCH_METHOD == "HIGH_SR":
                    delta_time = method2(SCOPE_ACQUISITION_TIME_OUT, Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)- Start_time
                NUMBER_ACQUISITIONS +=1
                Run = [NUMBER_ACQUISITIONS, delta_time]
                Result = []
                if MEAS_METHOD == "SCRIPT" and NUMBER_MEASUREMENTS > 0:
                    data = (KsInfiniiVisionX.query(str(MEAS_STRING)).split(';'))
                    Scope_Measurement_Results.append(Run + data)
                elif MEAS_METHOD == "SCOPE" and NUMBER_MEASUREMENTS > 0:
                    data = list(KsInfiniiVisionX.query(":MEASure:RESults?").split(','))
                    for m in range (1,NUMBER_MEASUREMENTS+1,1):
                        Result.append(float(data[((m-1)*2)+1]))
                    Scope_Measurement_Results.append(Run + Result)
                else:
                    Scope_Measurement_Results.append(Run)
                if PAUSE_BETWEEN_ACQUISISTIONS == "YES":
                    time.sleep(TIME_TO_PAUSE)

                if GET_SCREENSHOT == "EVERY":
                    Get_Screen(GENERATION,NUMBER_ACQUISITIONS)
                elif (GET_SCREENSHOT == "FIRST" or GET_SCREENSHOT == "FIRSTANDLAST") and NUMBER_ACQUISITIONS == 1:
                    Get_Screen(GENERATION,NUMBER_ACQUISITIONS)

            if int(len(Scope_Measurement_Results)) > 0 and NUMBER_MEASUREMENTS > 0:
                del m, delta_time, Start_time, Result, Run, data
            else:
                del delta_time, Start_time, Result, Run

        elif USE_AS_TRIGGER_TIME_RECORDER_ONLY == "YES":
            NUMBER_ACQUISITIONS = 0
            Start_time = time.clock()
            while (time.clock() - Start_time) < TIME_TO_RUN:
               RunResult= method1(SCOPE_ACQUISITION_TIME_OUT, Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)- Start_time
               NUMBER_ACQUISITIONS +=1
               Scope_Measurement_Results.append(RunResult)
               if PAUSE_BETWEEN_ACQUISISTIONS == "YES":
                   time.sleep(TIME_TO_PAUSE)
            del Start_time, RunResult

    if RUN_CONTROL_BY_TIME_OR_NUMBER == "TIME" and (GET_SCREENSHOT == "LAST" or GET_SCREENSHOT == "FIRSTANDLAST"):
        Get_Screen(GENERATION,NUMBER_ACQUISITIONS)

    if SYNCH_METHOD == "FAST":
        KsInfiniiVisionX.timeout = GLOBAL_TOUT

except KeyboardInterrupt:
    print 'Keyboard interupt.\n'
    print 'Attempting to save data...\n'
    if int(len(Scope_Measurement_Results)) > 0:
        Scope_Measurement_Results = Correct_Time_Stamps(Scope_Measurement_Results)
        Save_Data(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)
    IVScopeSafeExitCustomMessage("Properly closing scope and exiting script.")

except OSError as err:
    print 'Library error: ' + str(err.strerror) + str(err.message)
    print 'Attempting to save data...\n'
    if int(len(Scope_Measurement_Results)) > 0:
        Scope_Measurement_Results = Correct_Time_Stamps(Scope_Measurement_Results)
        Save_Data(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)
    IVScopeSafeExitCustomMessage("Properly closing scope and exiting script.")

except MemoryError as err:
    print 'Exception: MemoryError\n'
    print "This exception most likely occurred because the data array is too large."
    print "\t1: Use the script that saves data during the acquisition cycle.  This will reduce throughput somewhat."
    print 'Attempting to save data...\n'
    if int(len(Scope_Measurement_Results)) > 0:
        Scope_Measurement_Results = Correct_Time_Stamps(Scope_Measurement_Results)
        Save_Data(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)
    IVScopeSafeExitCustomMessage("Properly closing scope and exiting script. In some cases scope may already be closed: 'InvalidSession: Invalid session handle. The resource might be closed.'")

except Exception as err:
    print 'Exception: ' + str(err.message) + "\n"
    print "Generic error, possibly a timeout."
    print 'Attempting to save data...\n'
    if int(len(Scope_Measurement_Results)) > 0:
        try:
            Scope_Measurement_Results = Correct_Time_Stamps(Scope_Measurement_Results)
            Save_Data(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)
            IVScopeSafeExitCustomMessage("Properly closing scope and exiting script. In some cases scope may already be closed: 'InvalidSession: Invalid session handle. The resource might be closed.'")
        except Exception as err:
            print 'Exception: ' + str(err.message) + "\n"
            print "Generic error, possibly a timeout."
            print 'Attempting to save data...\n'
            Save_Data(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)
    else:
        print "No data to save."
    try:
        IVScopeSafeExitCustomMessage("Properly closing scope and exiting script. In some cases scope may already be closed: 'InvalidSession: Invalid session handle. The resource might be closed.'")
    except:
        if LOCK_SCOPE == "YES":
            print 'Scope connection lost. The scope front panel is likely locked.  Use Keysight IO Libraries connection expert to unlock it with :SYSTem:LOCK 0  You may need to re-enable the scope connection and do a device clear, as well as reset the Pythion interface.'
        else:
            print 'Scope connection lost. Use Keysight IO Libraries connection expert to unlock it with :SYSTem:LOCK 0  You may need to re-enable the scope connection and do a device clear, as well as reset the Pythion interface.'

##############################################################################################################################################################################
##############################################################################################################################################################################
## End Acquire and Measure Loop
##############################################################################################################################################################################
##############################################################################################################################################################################

##############################################################################################################################################################################
## Find time from trigger to final acquisition point, correct trigger time stamps
    ## For properly determining trigger times
    ## Currently NOT OK for average mode
if int(len(Scope_Measurement_Results)) > 0:
    if type(Scope_Measurement_Results) == list:
            Scope_Measurement_Results = np.asarray(Scope_Measurement_Results, dtype = float)
    SAMPLE_RATE_AND_POINTS = Get_SR_Points()
    Scope_Measurement_Results = Correct_Time_Stamps(Scope_Measurement_Results)
else:
    IVScopeSafeExitCustomMessage("No data acquired. Properly closing scope and exiting script.")

##############################################################################################################################################################################
## Properly disconnect from scope

print "Done with oscilloscope operations.\n"
KsInfiniiVisionX.clear() # Clear scope communications interface
KsInfiniiVisionX.write(":SYSTem:LOCK 0")
KsInfiniiVisionX.close() # Close communications interface to scope
## End properly disconnect from scope
##############################################################################################################################################################################

##############################################################################################################################################################################
## Save Data
Save_Data(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER)
## Save Data
##############################################################################################################################################################################

##############################################################################################################################################################################
## Done with scope - Statistics Reporting
do_stats(Scope_Measurement_Results, SCOPE_MEASUREMENT_HEADER,SAMPLE_RATE_AND_POINTS)
## Done with scope - Statistics Reporting
##############################################################################################################################################################################

##############################################################################################################################################################################
##############################################################################################################################################################################
## All Done
##############################################################################################################################################################################
##############################################################################################################################################################################

print "Done."

##############################################################################################################################################################################
##############################################################################################################################################################################
## End main script
##############################################################################################################################################################################
##############################################################################################################################################################################

##############################################################################################################################################################################
##############################################################################################################################################################################
## Addendum 1: Recalling data back into python
##############################################################################################################################################################################
##############################################################################################################################################################################

########################################################
## As CSV
########################################################

#filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Measurements.csv"
### read csv data back into python with:
#with open(filename, 'r') as filehandle: # r means open for reading
#    recalled_csv_data = np.loadtxt(filename,delimiter=',',skiprows=2)
#    ## The skiprows is to have it skip the header...
        ## Use skiprows = 2 if the acquistion mode is average or high res, or math is on, or if precision mode is on, or if synch method = HIGH_SR, as there is an additional header line.
        ## Use skiprows = 3 if math AND high res or average or precision mode also on...

########################################################
## As a NUMPY BINARY file
########################################################

#filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Measurements.npy"
### Read the NUMPY BINARY data back into python with:
#with open(filename, 'rb') as filehandle: # rb means open for reading binary
#    recalled_NPY_data = np.load(filehandle)
#    ## NOTE, if one were to not use with open, and just do np.save like this:
#            ## np.save(filename, np.vstack((DataTime,Data_Ch1)).T)
#            ## this method automatically appends a .npy to the file name...
#            ## no need for skip rows since there is no header...

##############################################################################################################################################################################
##############################################################################################################################################################################
## Addendum 2: Basic structure of this script
##############################################################################################################################################################################
##############################################################################################################################################################################

## Introduction
## Define Constants
## Do some error checks on constants
## Define some fucntions, most notably the acuisition synchronization fucntions
## Connect to scope and initialize
## Setup scope if method is by script - check for errors and safely abort on errors
## Calculate acquisition time out by gross overestimation
## Do some checks and adjustments on scope setup - check measurements
## Acquire loop
## get info from scope to Correct trigger timestamps and do it
    ## This COULD be done before the acquisition loop, but this requires a full acquisition, so in the interested of speed, it is done at the end.
## Save data.
## Error handling throughout, even in case of timeout or disconnect from scope.

##############################################################################################################################################################################
##############################################################################################################################################################################
## Addendum 3: Example of custom thresholds and zoom window/gating for
##############################################################################################################################################################################
##############################################################################################################################################################################

## Note: These are rather likely to cause "Data out of Range Errors" for a generic setup...

## This next line shows how to do specific thresholds
## M3 = ":MEASure:DEFine THResholds,ABSolute,2,1.15,0.25,CHANnel1;:MEASure:FREQuency? CHANnel1;:MEASure:DEFine THResholds,STANdard,CHANnel1" # Shows how to change thresholds and make a measurement with them.
## Note the threshold definition code and measurement is split with a semi-colon ;
## The thresholds go: Upper, middle, lower, where the measurement must go through all 3 points, and is made at the Middle threshold.
## Note that only timing measurements are affected by this.
## The :MEASure:TEDGE is not affected by :MEASure:DEFine THResholds.  The threshold for this is the 50% of Top and Base points with a bit of hysteresis added. You  cannot change the threshold definition.  Consider the TVLAUE measurement instead.
## IMPORTANT NOTE:
    ## When the loop starts over it will now have perhaps wrong thresholds for some other timing measurement on ch1 because of the above threshold definition.
    ## Thus, one may need to adjust/reset thresholds... for example: :MEASure:DEFine THResholds,STANdard,CHANnel1 is used (with a ;) to rese the thresholds

## This next line shows how to use the ZOOM WINDOW to gate a measurement
## M4 = ":TIMebase:MODE WINDow;:TIMebase:WINDow:RANGe 20.00E-06;:TIMebase:WINDow:POSition -250E-06;:MEASure:WINDow ZOOM;:MEASure:VAVerage?;:MEASure:WINDow MAIN;:TIMebase:MODE MAIN"
## It is performed like this:
    ##  Note everything was concatenated with semi-colons, as this speeds things up
    ## 1. Turn on zoom window with :TIMebase:MODE WINDow
    ## 2. Adjust width or range (total width) and then position of zoom window with :TIMebase:WINDow:Range 20.00E-06 and :TIMebase:WINDow:POSition -250E-06
        ## Note, for the ZOOM window, a negative position moves the window to the left, which is opposite the MAIN window behavior
        ## Need to adjust width or RANGe before the POSition as POSition can change when the RANGE is adjusted
    ## 3. Tell oscilloscope to apply measurements to Zoom window with :MEASure:WINDow ZOOM
    ## 4. Make measurement (adjust thresholds as needed)
    ## 5. Tell oscilloscope to go back to making measurements on main time window with :MEASure:WINDow MAIN
    ## 6. Turn off zoom window (really, turning of the zoom window takes care of step 5, but is left in for clarity and robustness) with :TIMebase:MODE MAIN
    ## On the X4000A, X3000T, and X6000A, it is possible to gate measurements with the cursors: use :MEASure:WINDow GATE instead of :MEASure:WINDow ZOOM, and setup the marker X1 and X2 positions

## This next measurement shows how to do a delay measurement on 2 channels with custom thresholds for each
## M5 = ":MEASure:DEFine THResholds,ABSolute,2.6,1,0.3,CHANnel1;:MEASure:DEFine THResholds,ABSolute,2,0.5,.3,CHANnel3;:MEASure:DEFine DELay,3,-1;:MEASure:DELay? CHANNEL1,CHANNEL3;:MEASure:DEFine THResholds,STANdard,CHANnel1"
    ## Defines absolute upper, middle, then lower threshold voltages (in that order) on channels 1 and then different ones on channel 3
        ## :MEASure:DEFine THResholds,ABSolute,2.6,1,0.3,CHAN1
        ## :MEASure:DEFine THResholds,ABSolute,2,0.5,.3,CHAN2
    ## Defines the edges for the delay measurement as the 3rd rising edge on the first channel, and the first falling edge on the second channel
        ## :MEASure:DEFine DELay,3,-1
        ## NOTE: If there is an edge close to the left side of the screen, it may not count it…. So do some tests first, of course
    ## Actually measure delay with: :MEASure:DELay? CHANNEL1,CHANNEL3
    ## Reset thresholds... (reset delay definition if needed)

## MEASURE_LIST = [M1, M2, M3, M4, M5]
## SCOPE_MEASUREMENT_HEADER = "Vpeak-peak CH1 (V),Frequency CH1 (Hz), Frequency CH1 with custom thresholds (Hz), Gated Vavg CH3 (V), Delay CH1-CH3 (s)"