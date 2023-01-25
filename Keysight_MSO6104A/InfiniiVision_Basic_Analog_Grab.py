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
import pyvisa
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

## In general, this script shows how to pull the waveform data from the analog channels for already acquired data, and save it to a computer.
## More specifically, it shows how to determine which channels are on and have data, how much data, get the data into an array, scale data for each channel,
## and save/recall it to/from disk in both csv and Python numpy formats.  Methods for getting ALL or just some data are shown in addenda.
## This script should work for all InfiniiVision and InfiniiVision-X oscilloscopes:
## DSO5000A, DSO/MSO6000A/L, DSO/MSO7000A/B, DSO/MSO-X2000A, DSO/MSO-X3000A/T, DSO/MSO-X4000A, DSO/MSO-X6000A

## NO ERROR CHECKING OR HANDLING IS INCLUDED

##  ALWAYS DO SOME TEST RUNS!!!!! and ensure you are getting what you want and it is later usable!!!!!

## INSTRCUTIONS:
## Edit in the VISA address of the oscilloscope
## Edit in the file save locations ## IMPORTANT NOTE:  This script WILL overwrite previously saved files!
## Manually (or write more code) acquire data on the oscilloscope.  Ensure that it finished.

##############################################################################################################################################################################
##############################################################################################################################################################################
## DEFINE CONSTANTS
##############################################################################################################################################################################
##############################################################################################################################################################################

## Initialization constants
VISA_ADDRESS = "'TCPIP0::192.168.4.12::INSTR'" # Get this from Keysight IO Libraries Connection Expert #Note: sockets are not supported in this revision of the script, and pyVisa 1.6.3 does not support HiSlip
GLOBAL_TOUT =  10000 # IO time out in milliseconds

## Save Locations
BASE_FILE_NAME = "my_data"
BASE_DIRECTORY = "C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\MSO6104A"
    ## IMPORTANT NOTE:  This script WILL overwrite previously saved files!

##############################################################################################################################################################################
##############################################################################################################################################################################
## Main code
##############################################################################################################################################################################
##############################################################################################################################################################################

sys.stdout.write("Script is running.  This may take a while...")

##############################################################################################################################################################################
##############################################################################################################################################################################
## Connect and initialize scope
##############################################################################################################################################################################
##############################################################################################################################################################################

## Define VISA Resource Manager & Install directory
## This directory will need to be changed if VISA was installed somewhere else.
rm = pyvisa.ResourceManager() # this uses pyvisa  'C:\\Windows\\System32\\visa32.dll'
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

## DO NOT RESET THE SCOPE! - since that would wipe out data...

## Data should already be acquired and scope should be STOPPED

##############################################################################################################################################################################
##############################################################################################################################################################################
## Determine which channels are on, and which have acquired data, and get the vertical pre-amble info accordingly
## For repetitive acquisitions, this only needs to be done once unless settings are changed
    ## Use brute force method for readability
##############################################################################################################################################################################
##############################################################################################################################################################################

CHS_ON = [0,0,0,0] # Create empty array to store channel states
NUMBER_CHANNELS_ON = 0
## These above items are for a more elegant method of pulling and scaling the waveform data below...

## Determine Acquisition Mode
ACQ_TYPE = str(KsInfiniiVisionX.query(":ACQuire:TYPE?")).strip("\n")
        ## This can normally be done later (when pulling pre-ambles) or is known, but since the script is supposed to find everything, it is done now...
if ACQ_TYPE == "AVER" or ACQ_TYPE == "AVER" or ACQ_TYPE == "AVERage":
    POINTS_MODE = "NORMal" # Use for Average acquisition mode
else:
    POINTS_MODE = "RAW" # Use for every acquisition mode besides Average

## Set points mode for determining which channels are on and have data - Points mode is later reset
KsInfiniiVisionX.write(":WAVeform:POINts:MODE " + str(POINTS_MODE)) # Otherwise this is normally done when setting up the waveform export.
    ## If average mode is used, this must be set to NORMal, as the below points queries will return 0 points even if there are points if RAW is used.

## Channel 1
on_off = int(KsInfiniiVisionX.query(":CHANnel1:DISPlay?"))
Channel_acquired = int(KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel1;:WAVeform:POIN?")) # If this returns a zero, then this channel did not capture data and thus there are no points (but was turned on after the acquisition for some reason)
if Channel_acquired == 0 or on_off == 0:
    KsInfiniiVisionX.write(":CHANnel1:DISPlay OFF") # Setting a channel to be a waveform source turns it on...
    CHS_ON[0] = 0 # Recall that python indices start at 0, so ch1 is index 0
    Y_INCrement_Ch1 = "BLANK"
    Y_ORIGin_Ch1    = "BLANK"
    Y_REFerence_Ch1 = "BLANK"
else:
    CHS_ON[0] = 1
    NUMBER_CHANNELS_ON += 1
    Pre = KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel1;:WAVeform:PREamble?").split(',')
    Y_INCrement_Ch1 = float(Pre[7]) # Voltage difference between data points
    Y_ORIGin_Ch1    = float(Pre[8]) # Voltage at center screen
    Y_REFerence_Ch1 = float(Pre[9]) # Specifies the data point where y-origin occurs, always zero
        ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.
    ## In most cases this will need to be done for each channel as the ve5rtical scale and offset will differ. However, 
        ## if the vertical scales and offset are identical, the values for one channel can be used for the others.
        ## For math waveforms, this should always be done.

## Channel 2
on_off = int(KsInfiniiVisionX.query(":CHANnel2:DISPlay?"))
Channel_acquired = int(KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel2;:WAVeform:POIN?"))
if Channel_acquired == 0 or on_off == 0:
    KsInfiniiVisionX.write(":CHANnel2:DISPlay OFF")
    CHS_ON[1] = 0
    Y_INCrement_Ch2 = "BLANK"
    Y_ORIGin_Ch2    = "BLANK"
    Y_REFerence_Ch2 = "BLANK"
else:
    CHS_ON[1] = 1
    NUMBER_CHANNELS_ON += 1
    Pre = KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel2;:WAVeform:PREamble?").split(',')
    Y_INCrement_Ch2 = float(Pre[7])
    Y_ORIGin_Ch2    = float(Pre[8])
    Y_REFerence_Ch2 = float(Pre[9])

## Channel 3
on_off = int(KsInfiniiVisionX.query(":CHANnel3:DISPlay?"))
Channel_acquired = int(KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel3;:WAVeform:POIN?"))
if Channel_acquired == 0 or on_off == 0:
    KsInfiniiVisionX.write(":CHANnel3:DISPlay OFF")
    CHS_ON[2] = 0
    Y_INCrement_Ch3 = "BLANK"
    Y_ORIGin_Ch3    = "BLANK"
    Y_REFerence_Ch3 = "BLANK"
else:
    CHS_ON[2] = 1
    NUMBER_CHANNELS_ON += 1
    Pre = KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel3;:WAVeform:PREamble?").split(',')
    Y_INCrement_Ch3 = float(Pre[7])
    Y_ORIGin_Ch3    = float(Pre[8])
    Y_REFerence_Ch3 = float(Pre[9])

## Channel 4
on_off = int(KsInfiniiVisionX.query(":CHANnel4:DISPlay?"))
Channel_acquired = int(KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel4;:WAVeform:POIN?"))
if Channel_acquired == 0 or on_off == 0:
    KsInfiniiVisionX.write(":CHANnel4:DISPlay OFF")
    CHS_ON[3] = 0
    Y_INCrement_Ch4 = "BLANK"
    Y_ORIGin_Ch4    = "BLANK"
    Y_REFerence_Ch4 = "BLANK"
else:
    CHS_ON[3] = 1
    NUMBER_CHANNELS_ON += 1
    Pre = KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel4;:WAVeform:PREamble?").split(',')
    Y_INCrement_Ch4 = float(Pre[7])
    Y_ORIGin_Ch4    = float(Pre[8])
    Y_REFerence_Ch4 = float(Pre[9])

if NUMBER_CHANNELS_ON == 0:
    KsInfiniiVisionX.clear()
    KsInfiniiVisionX.close()
    sys.exit("No data has been acquired. Properly closing scope and aborting script.")

## ANALOGVERTPRES is used for a more elegant method of pulling and scaling the waveform data below...
## Otherwise use the individual scale factors
ANALOGVERTPRES = (Y_INCrement_Ch1, Y_INCrement_Ch2, Y_INCrement_Ch3, Y_INCrement_Ch4, Y_ORIGin_Ch1, Y_ORIGin_Ch2, Y_ORIGin_Ch3, Y_ORIGin_Ch4, Y_REFerence_Ch1, Y_REFerence_Ch2, Y_REFerence_Ch3, Y_REFerence_Ch4)
del Pre, on_off, Channel_acquired

## Find first channel on (as needed/desired)
ch = 1
for each_value in CHS_ON:
    if each_value == 1:
        FIRST_CHANNEL_ON = ch
        break
    ch +=1
del ch, each_value

## Find last channel on (as needed/desired)
ch = 1
for each_value in CHS_ON:
    if each_value ==1:
        LAST_CHANNEL_ON = ch
    ch +=1
del ch, each_value

##############################################################################################################################################################################
##############################################################################################################################################################################
## Setup data export - For repetitive acquisitions, this only needs to be done once unless settings are changed
##############################################################################################################################################################################
##############################################################################################################################################################################

KsInfiniiVisionX.write(":WAVeform:FORMat WORD")    # 16 bit word format... or BYTE for 8 bit format - WORD recommended, see more comments below when the data is actually retrieved
KsInfiniiVisionX.write(":WAVeform:BYTeorder LSBFirst") # Explicitly set this to avoid confusion
KsInfiniiVisionX.write(":WAVeform:UNSigned 0") # Explicitly set this to avoid confusion
## Next command is already done in this particular script
#KsInfiniiVisionX.write(":WAVeform:POINts:MODE " + str(TYPE)) # Set this now so when the preamble is queried it knows what how many points it can retrieve from
    ## If measurements are also being made, they are made on a different record, the "measurement record."  This record can be accessed by using:
    ## :WAVeform:POINts:MODE NORMal isntead of :WAVeform:POINts:MODE RAW
KsInfiniiVisionX.write(":WAVeform:SOURce CHANnel" + str(FIRST_CHANNEL_ON)) # Set waveform source to any enabled channel, here the FIRST_CHANNEL_ON
KsInfiniiVisionX.write(":WAVeform:POINts MAX") # Set number of points to max possible for any InfiniiVision; ensures all are available
    ## The MAX command here also changes the mode to MAX, which may or may not be a good thing, so change it to what is needed:
KsInfiniiVisionX.write(":WAVeform:POINts:MODE " + str(POINTS_MODE))    
POINTS = int(KsInfiniiVisionX.query(":WAVeform:POINts?")) ## Now get number of points.  This is the number of points currently available - this is for on screen data only - Will not change channel to channel.
    ## NOTES:
        ## For getting ALL of the data off of the scope, as opposed to just what is on screen, see Addendum 1
        ## For getting LESS data than is on screen, see Addendum 2
        ## For getting ONLY CERTAIN data points, see Addendum 3
        ## The methods shown in these addenda are combinable

## Get timing pre-amble data
Pre = KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',')
## While these values can always be used for all analog channels, they need to be retrieved and used separately for math/other waveforms as they will likely be different.
#ACQ_TYPE    = float(Pre[1]) # Gives the scope acquisition mode; this is already done above in this particular script
X_INCrement = float(Pre[4]) # Time difference between data points
X_ORIGin    = float(Pre[5]) # Always the first data point in memory
X_REFerence = float(Pre[6]) # Specifies the data point associated with x-origin; The x-reference point is the first point displayed and XREFerence is always 0.
    ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.
del Pre

## Pre-allocate data array - for a more elegant method of pulling and scaling the waveform data below...
Wav_Data = np.zeros([NUMBER_CHANNELS_ON,POINTS])

## Pre-allocate data array - for a more elegant method of pulling and scaling the waveform data below...
if ACQ_TYPE == "PEAK": # This means peak detect mode
    Wav_Data = np.zeros([NUMBER_CHANNELS_ON,2*POINTS])
    ## Peak detect mode returns twice as many points as the points query, one point each for LOW and HIGH values
else: # For all other acquistion modes
    Wav_Data = np.zeros([NUMBER_CHANNELS_ON,POINTS])

##############################################################################################################################################################################
##############################################################################################################################################################################
## Create time axis - For repetitive acquisitions, this only needs to be done once unless settings are changed
##############################################################################################################################################################################
##############################################################################################################################################################################
DataTime = ((np.linspace(0,POINTS-1,POINTS)-X_REFerence)*X_INCrement)+X_ORIGin
if ACQ_TYPE == "PEAK": # This means peak detect mode
    DataTime = np.repeat(DataTime,2)
    ##  The points come out as Low(time1),High(time1),Low(time2),High(time2)....

##############################################################################################################################################################################
##############################################################################################################################################################################
## Pull waveform data, scale it
## Brute Force method
##############################################################################################################################################################################
##############################################################################################################################################################################

## Channel 1
## If on, pull data
if CHS_ON[0] == 1: # Recall that python indices start at 0, so ch1 is index 0
    ## Gets the waveform in 16 bit WORD format
    Data_Ch1 = np.array(KsInfiniiVisionX.query_binary_values(':WAVeform:SOURce CHANnel1;DATA?', "h", False))
    ## for BYTE format, use "b" instead of "h"
            ## WORD is more accuruate, but slower for long records, say over 100 kPts
            ## WORD strongly suggested for average and High Res acquisition modes.
        ## for MSBFirst use TRUE (Don't use MSBFirst unless that is the computer architecture - most common machines are LSBF)
        ## Notice that the waveform source is specified, and the actual data query is concatenated into one line with a semi-colon (;) essentially like this:
            ## :WAVeform:SOURce CHANnel1;DATA?
            ## This makes it "go" a little faster.
        ## One can easily setup a save after each waveform grab in this brute force method for repetitive acquisitions

    ## Scales the waveform
    Data_Ch1 = ((Data_Ch1-Y_REFerence_Ch1)*Y_INCrement_Ch1)+Y_ORIGin_Ch1

## Channel 2
if CHS_ON[1] == 1:
    Data_Ch2 = np.array(KsInfiniiVisionX.query_binary_values(':WAVeform:SOURce CHANnel2;DATA?', "h", False))
    Data_Ch2 = ((Data_Ch2-Y_REFerence_Ch2)*Y_INCrement_Ch2)+Y_ORIGin_Ch2

## Channel 3
if CHS_ON[2] == 1:
    Data_Ch3 = np.array(KsInfiniiVisionX.query_binary_values(':WAVeform:SOURce CHANnel3;DATA?', "h", False))
    Data_Ch3 = ((Data_Ch3-Y_REFerence_Ch3)*Y_INCrement_Ch3)+Y_ORIGin_Ch3

## Channel 4
if CHS_ON[3] == 1:
    Data_Ch4 = np.array(KsInfiniiVisionX.query_binary_values(':WAVeform:SOURce CHANnel4;DATA?', "h", False))
    Data_Ch4 = ((Data_Ch4-Y_REFerence_Ch4)*Y_INCrement_Ch4)+Y_ORIGin_Ch4


##############################################################################################################################################################################
##############################################################################################################################################################################
## Pull waveform data, scale it
## A more elegant method
##############################################################################################################################################################################
##############################################################################################################################################################################

ch = 1 # channel number
i  = 0 # index of Wav_data, recall that python indices start at 0, so ch1 is index 0
for each_value in  CHS_ON:
    if each_value == 1:
        ## Gets the waveform in 16 bit WORD format
        Wav_Data[i,:] = np.array(KsInfiniiVisionX.query_binary_values(':WAVeform:SOURce CHANnel' + str(ch) + ';DATA?', "h", False))
        ## for BYTE format, use "b" instead of "h"
            ## WORD is more accuruate, but slower for long records, say over 100 kPts
            ## WORD strongly suggested for average and High Res acquisition modes.
        ## for MSBFirst use TRUE (Don't use MSBFirst unless that is the computer architecture - most common machines are LSBF)
        ## Notice that the waveform source is specified, and the actual data query is concatenated into one line with a semi-colon (;) essentially like this:
            ## :WAVeform:SOURce CHANnel1;DATA?
            ## This makes it "go" a little faster.
        ## This method can fail IF the acquisition mode is changed AFTER the signal is acquired, and a new acq is not taken.
            ## This happened because the Wav_Data array has been pre-allocated.
            ## The brute force method does not suffer this.  The error message associated with this will look like:
            ## ValueError: could not broadcast input array from shape (400000) into shape (200000)

        ## Scales the waveform
        Wav_Data[i,:] = ((Wav_Data[i,:]-ANALOGVERTPRES[ch+7])*ANALOGVERTPRES[ch-1])+ANALOGVERTPRES[ch+3]
            ## For clarity: Scaled_waveform_Data[*] = [(Unscaled_Waveform_Data[*] - Y_reference) * Y_increment] + Y_origin
        i +=1
    ch +=1
del ch, i, each_value

##############################################################################################################################################################################
##############################################################################################################################################################################
## Close Connection to scope properly
##############################################################################################################################################################################
##############################################################################################################################################################################
KsInfiniiVisionX.clear()
KsInfiniiVisionX.close()


##############################################################################################################################################################################
##############################################################################################################################################################################
## Save waveform data - for brute force method  - really, there are MANY ways to do this, of course
##############################################################################################################################################################################
##############################################################################################################################################################################

## Channel 1
## If on, save data
if CHS_ON[0] == 1: # Recall that python indices start at 0, so ch1 is index 0
    ########################################################
    ## As CSV - easy to deal with later, but slow and large
    ########################################################
    header = "Time (s),Channel 1 (V)\n"
    now = time.clock() # Only to show how long it takes to save
    filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Channel1.csv"
    ## Using: with open takes care of a lot of stuff, and no need to explicitly close
    with open(filename, 'w') as filehandle: # w means open for writing; can overwrite
        filehandle.write(header)
        np.savetxt(filehandle, np.vstack((DataTime,Data_Ch1)).T, delimiter=',')
            ## np.vstack basically concatenates the timing info and analog data into one array, but it will be shape (2 rows, NPoints columns),
            ## and typically one wants (NPoints rows,2 columns), and the .T (transpose) at the end takes care of that
    print ("It took " + str(time.clock() - now) + " seconds to save 1 channel in csv format.")
    del now

    ## Read the csv data back into python with:
    with open(filename, 'r') as filehandle: # r means open for reading
        recalled_brute_force_csv_ch1 = np.loadtxt(filehandle,delimiter=',',skiprows=1) # Skiprows keeps it from pulling the header in

    del filehandle, filename, header

    ########################################################
    ## As a NUMPY BINARY file - fast and small, but really only good for python - can't use header
    ########################################################
    now = time.clock() # Only to show how long it takes to save
    filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Channel1.npy"
    with open(filename, 'wb') as filehandle: # wb means open for writing in binary; can overwrite
        np.save(filehandle, np.vstack((DataTime,Data_Ch1)).T) # See comment above regarding np.vstack and .T
        ## NOTE, if one were to not use with open, and just do np.save like this:
            ## np.save(filename, np.vstack((DataTime,Data_Ch1)).T)
            ## this method automatically appends a .npy to the file name...
    print ("It took " + str(time.clock() - now) + " seconds to save 1 channel in binary format.")
    del now

    ## Read the NUMPY BINARY data back into python with:
    with open(filename, 'rb') as filehandle: # rb means open for reading binary
        recalled_brute_force_NPY_ch1 = np.load(filehandle)

## Repeat as needed...
## Channel 2
## Channel 3
## Channel 4

del filename, filehandle

##############################################################################################################################################################################
##############################################################################################################################################################################
## Save waveform data - for elegant method - really, there are MANY ways to do this, of course
##############################################################################################################################################################################
##############################################################################################################################################################################

########################################################
## As CSV - easy to deal with later, but slow and large
########################################################
## Create header
header = "Time (s),"
ch = 1
for each_value in CHS_ON:
    if each_value == 1:
        if ch == LAST_CHANNEL_ON:
            header = header + "Channel " + str(ch) + " (V)\n"
        else:
            header = header + "Channel " + str(ch) + " (V),"
    ch +=1
del each_value, ch

## Save data
now = time.clock() # Only to show how long it takes to save
filename = BASE_DIRECTORY + BASE_FILE_NAME + ".csv"
with open(filename, 'w') as filehandle: # w means open for writing; can overwrite
    filehandle.write(header)
    np.savetxt(filehandle, np.insert(Wav_Data,0,DataTime,axis=0).T, delimiter=',')
        ## The np.insert essentially deals with the fact that Wav_Data is a multi-dimensional array and DataTime is a
        ## 1 1D array, and cannot otherwise be concatenated easily.  As described above, the .T is a transpose
print ("It took " + str(time.clock() - now) + " seconds to save " + str(NUMBER_CHANNELS_ON) + " channels in csv format.")
del now

## Read csv data back into python with:
with open(filename, 'r') as filehandle: # r means open for reading
    recalled_csv_data = np.loadtxt(filename,delimiter=',',skiprows=1)

del filehandle, filename, header

########################################################
## As a NUMPY BINARY file - fast and small, but really only good for python - can't use header
########################################################
now = time.clock() # Only to show how long it takes to save
filename = BASE_DIRECTORY + BASE_FILE_NAME + ".npy"
with open(filename, 'wb') as filehandle: # wb means open for writing in binary; can overwrite
    np.save(filehandle, np.insert(Wav_Data,0,DataTime,axis=0).T)
print ("It took " + str(time.clock() - now) + " seconds to save " + str(NUMBER_CHANNELS_ON) + " channels in binary format.")
del now

## Read the NUMPY BINARY data back into python with:
with open(filename, 'rb') as filehandle: # rb means open for reading binary
    recalled_NPY_data = np.load(filehandle)
    ## NOTE, if one were to not use with open, and just do np.save like this:
            ## np.save(filename, np.vstack((DataTime,Data_Ch1)).T)
            ## this method automatically appends a .npy to the file name...

del filename, filehandle

##############################################################################################################################################################################
##############################################################################################################################################################################
## Done - cleanup
##############################################################################################################################################################################
##############################################################################################################################################################################

print ("Done.")

##############################################################################################################################################################################
##############################################################################################################################################################################
## Addendum 1, For getting ALL of the data off of the scope, as opposed to just what is on screen
## The methods shown in these addenda are combinable
##############################################################################################################################################################################
##############################################################################################################################################################################

## The InfiniiVision scopes ONLY pull data from what is available on screen. Thus, if data was acquired at a short time scale,
    ## data may be available off screen.  It can easily be brought on screen by setting the time scale to something very large.
    ## However, in certain cases (long time scale initial captures with large positions), the time position and time reference can
    ## cause data to still be off screen.  The below can take care of all of this.
## This method IS NOT recommended for :WAVeform:POINts:MODE NORMAL.
    ## NORMAL is the so called measurement record which is almost always shorter than the RAW record, and will result in an aliased waveform
    ## If the measurement record is desired, don't even bother with this...
## This method IS NOT suggested for High-Resolution and Average acquisition modes as changing the time scale can change the waveform in these modes.

### Determine initial time base settings for later re-use
#TimeScale = float(KsInfiniiVisionX.query(":TIMebase:SCALe?"))
#TimePosition = float(KsInfiniiVisionX.query(":TIMebase:POSition?"))
#TimeReference = str(KsInfiniiVisionX.query(":TIMebase:REFerence?")).strip("\n")
#if TimeReference == ("CENT" or "CENTer"):
#    TimeReference = "CENTer"
#elif TimeReference == ("RIGH" or "RIGHt"):
#    TimeReference = "RIGHt"
#
### Bring data on screen for any initial time  base setup
#if TimeReference == ("RIGHt") and (TimePosition < -50.0) and (TimeScale  > 20.0):
#    KsInfiniiVisionX.write(":TIMebase:SCALe 50;POSition -50 S") # This ensures that all data will be available in this scenario
#elif TimeReference == ("CENTer") and (TimePosition < -250.0) and (TimeScale  > 20.0):
#    KsInfiniiVisionX.write(":TIMebase:SCALe 50;POSition -250 S") # This ensures that all data will be available in this scenario
#elif TimeReference == ("LEFT") and (TimePosition < -450.0) and (TimeScale  > 20.0):
#    KsInfiniiVisionX.write(":TIMebase:SCALe 50;POSition -450 S") # This ensures that all data will be available in this scenario
#else:
#    KsInfiniiVisionX.write(":TIMebase:SCALe 50")# This ensures that all data will be available in this scenario
#
### Determine # of points and pre-amble info
#KsInfiniiVisionX.write(":WAVeform:POINts 8000000") # Set number of points to max possible for any InfiniiVision; ensures all are available
#    ## This above line may throw a "Data out of range error."  Ignore it.  The next line clears it.
#KsInfiniiVisionX.query(":SYSTem:ERRor?")
#POINTS = int(KsInfiniiVisionX.query(":WAVeform:POINts?")) ## Get number of points.
### Pre-allocate data array - for a more elegant method of pulling and scaling the waveform data below...
#Wav_Data = np.zeros([NUMBER_CHANNELS_ON,POINTS])
#
### Get timing pre-amble data
#Pre = KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',')
#X_INCrement = float(Pre[4]) # Time difference between data points
#X_ORIGin    = float(Pre[5]) # Always the first data point in memory
#X_REFerence = float(Pre[6]) # Specifies the data point associated with x-origin; The x-reference point is the first point displayed and XREFerence is always 0.
#del Pre
#
### Proceed as normal, get data and whatnot...
#
### Reset time base as desired/needed (after pulling data) - Do it in this order
#KsInfiniiVisionX.write(":TIMebase:REFerence " + str(TimeReference))
#KsInfiniiVisionX.write(":TIMebase:SCALe " + str(TimeScale))
#KsInfiniiVisionX.write(":TIMebase:POSition " + str(TimePosition))
#KsInfiniiVisionX.query("*OPC?")

##############################################################################################################################################################################
##############################################################################################################################################################################
## Addendum 2, For getting LESS data than is on screen
## The methods shown in these addenda are combinable
##############################################################################################################################################################################
##############################################################################################################################################################################

## Sometimes one may wish to get fewer than the available number of points. This is accomplished by:
    ## Asking the scope how many points are available.
    ## Telling it how many are desired (less than are available)
    ## Ask it again how many points, and use that many points. It may not be the number asked for, for various reasons.

#KsInfiniiVisionX.write(":WAVeform:POINts 8000000") # Set number of points to max possible for any InfiniiVision; ensures all are available
#    ## This above line may throw a "Data out of range error."  Ignore it.  The next line clears it.
#KsInfiniiVisionX.query(":SYSTem:ERRor?")
#POINTS_ON_SCREEN = int(KsInfiniiVisionX.query(":WAVeform:POINts?")) # Get number of points.  This is the number of points currently available - this is for on screen data only.
#POINTS_DESIRED = 100
#KsInfiniiVisionX.write(":WAVeform:POINts " + str(POINTS_DESIRED)) # Set number of points desired
#POINTS_TO_USE = int(KsInfiniiVisionX.query(":WAVeform:POINts?")) # After telling the scope how many points are desired, this is how many are available
### Proceed as normal

##############################################################################################################################################################################
##############################################################################################################################################################################
## Addendum 3, For getting ONLY CERTAIN data points
## The methods shown in these addenda are combinable
##############################################################################################################################################################################
##############################################################################################################################################################################

## It may sometimes be useful to only grab certain parts of a waveform.  This can be accomplished using the ZOOM window.
## Basically all that is needed is to turn it on, and adjust the width to contain only the desired data, and put it where it is needed...
    ## However, it is worth noting that this essentially uses :WAVeform:POINts:MODE NORMal, as opposed to RAW, and it is just as easy to
    ## NOT use the zoom window to the same effect (still need to change timing, not vertical, pre-ambles)...

#KsInfiniiVisionX.write(":TIMebase:MODE WINDow") # Turns zoom window on - do this first
#KsInfiniiVisionX.write(":TIMebase:WINDow:Range 20.00E-06") # Adjust width of window - do this second - this is the total width, not the scale (i.e. it is 10x the scale)
#KsInfiniiVisionX.write(":TIMebase:WINDow:POSition -250E-06") # Moves zoom window left/right - do this third - if it is done in opposite order, the POSition can change when the RANGE is adjusted
#    ## Note, for the ZOOM window, a negative position moves the window to the left, which is opposite the MAIN window behavior
#KsInfiniiVisionX.write(":WAVeform:SOURce CHANnel" + str(FIRST_CHANNEL_ON)) # Set waveform source to some enabled channel. Will not change channel to channel.
#POINTS_ZOOM_1 = int(KsInfiniiVisionX.query(":WAVeform:POINts?")) # Get the number of points available for THIS ZOOM window
### Get timing pre-amble data for THIS ZOOM window
#Pre = KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',')
#X_INCrement_ZOOM_1 = float(Pre[4])
#X_ORIGin_ZOOM_1    = float(Pre[5])
#X_REFerence_ZOOM_1 = float(Pre[6])
### Note that vertical pre-ambles do not change with this.
#del Pre
### Create time axis for THIS zoom window
#DataTime_ZOOM_1 = ((np.linspace(0,POINTS_ZOOM_1-1,POINTS_ZOOM_1)-X_REFerence_ZOOM_1)*X_INCrement_ZOOM_1)+X_ORIGin_ZOOM_1
#
### Pull and scale data... as per main script
#
### Do a second zoom window...
#KsInfiniiVisionX.write(":TIMebase:WINDow:Range 50.00E-06")
#KsInfiniiVisionX.write(":TIMebase:WINDow:POSition 100E-06")
#KsInfiniiVisionX.write(":WAVeform:SOURce CHANnel" + str(FIRST_CHANNEL_ON))
### Getting the timing pre-amble for NEW zoom window...
#POINTS_ZOOM_2 = int(KsInfiniiVisionX.query(":WAVeform:POINts?"))
#Pre = KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',')
#X_INCrement_ZOOM_2 = float(Pre[4])
#X_ORIGin_ZOOM_2    = float(Pre[5])
#X_REFerence_ZOOM_2 = float(Pre[6])
### Note that vertical pre-ambles do not change with this.
#del Pre
### Create time axis for THIS zoom window
#DataTime_ZOOM_2 = ((np.linspace(0,POINTS_ZOOM_2-1,POINTS_ZOOM_2)-X_REFerence_ZOOM_2)*X_INCrement_ZOOM_2)+X_ORIGin_ZOOM_2
#
### Pull and scale data... as per main script
#
### Set time window back to main
#KsInfiniiVisionX.write(":TIMebase:MODE MAIN")
#    ## Note that if the zoom window is turned back on, it will revert to the last settings it had, not default