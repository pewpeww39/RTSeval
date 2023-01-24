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
## This script can get waveforms, and measurements from analog channels for segmented memory already acquired on an InfiniiVision Scope.  It can also get time tags and produce an averaged segment for each analog channel.
## This script assumes the user has already acquired segments manually on an InfiniiVision or InfiniiVision-X oscilloscope.  A license may be needed for segmented memory.
## The user must make some trivial edits as per below instructions.
## The script figures out how many segments were actually acquired, flips through them, gathers the:
    ## time tags and/or
    ## desired measurement results that the user has edited in and/or
    ## waveforms from all enabled analog channels.
## Saves results to a csv file(s), which is openable in Microsoft XL and just about any other software…
## Script defaults should work for any 4 channel InfiniiVision or InfiniiVision-X oscilloscope with:
    ## Channels 1 & 3 hooked to the probe compensation port with a passive probe
    ## Channels 1 & 3 on, and AutoScaled
    ## Results placed in C:\Users\Public\ w/ file name my_data.csv (editable)
## User enables segmented memory and acquires a few segments
## This script should work for all InfiniiVision and InfiniiVision-X oscilloscopes:
## DSO5000A, DSO/MSO6000A/L, DSO/MSO7000A/B, DSO/MSO-X2000A, DSO/MSO-X3000A/T, DSO/MSO-X4000A, DSO/MSO-X6000A
## Tested against MSOX3104A w/ Firmware System Version 2.39, and MSO6054A w/ Systerm Version 6.20.0000
## segmented memory video: https://www.youtube.com/watch?v=riYGdiNG2PU
## NO ERROR CHECKING OR HANDLING IS INCLUDED

## INSTRUCTIONS
## 1. Setup oscilloscope and acquire segments manually, wait until acquisition is done
## The following applies to this script under ## Initialization constants, just below these instructions
## 2. Modify VISA address; Get VISA address of oscilloscope from Keysight IO Libraries Connection Expert
## 3. Enable analog waveform saving or not.
## 3.1 Enable averaged waveform or not.
## 4.0 Enable measurements or not.
## 4.1 Enter number of measurements to take per segment under N_MEASUREMENTS
    ## At least 1 measurement MUST be enabled if measurements are enabled
## 4.2 Edit measurement header info below (MeasHeader)
## 5. Enable saving of time tags to separate file or not
## 6. Edit BASE_FILE_NAME and BASE_DIRECTORY under ## Save Locations
    ## IMPORTANT NOTE:  This script WILL overwrite previously saved files!
## 7. Edit/add/remove measurements to retrieve at ## FLAG_DEFINE_MEASUREMENTS – refer to oscilloscope programmer's guide as needed
    ## Note that desired measurements can potentially be configured to turn on channels that were otherwise off.
    ## This could potentially cause a timeout error in a few places when trying to get the waveform data, but
    ## this is taken care of.  What IS NOT taken care of is bad measurements commands.  Try them out in Keysight Connection Expert or Command Expert first
## 8. ALWAYS DO SOME TEST RUNS!!!!! and ensure you are getting what you want and it is later usable!!!!!

##############################################################################################################################################################################
##############################################################################################################################################################################
## DEFINE CONSTANTS
##############################################################################################################################################################################
##############################################################################################################################################################################

## Initialization constants
VISA_ADDRESS = "USB0::0x0957::0x17A0::MY51500437::0::INSTR" # Get this from Keysight IO Libraries Connection Expert #Note: sockets are not supported in this revision of the script, and pyVisa 1.6.3 does not support HiSlip
GLOBAL_TOUT =  10000 # IO time out in milliseconds

## Pull waveform data?
GET_WFM_DATA = "YES" # "YES" or "NO" ; Automatically determines which analog channels are on, and grabs the waveform data for each segment.
    ## If you do not want to pull that channel data, turn it off, though it must be on for a measurement.
    ## One time axis is created for ALL segments, so each segment is referenced to its own trigger.
    ## One file per analog channel is created, with every segment, time tags, and segment indices.
DO_AVERAGE = "YES" # "YES" or "NO" ; create an averaged waveform for each analog channel.  It is placed in the final column of the resulting data file..
    ## This is not done on-board the scope.  It is done in this script.

## Perform and get measurements?
DO_MEASUREMENTS = "YES" # "YES" or "NO" ; Performs measurements for each segment.  Measurements are to be set up in
    ## this script, and not on the scope.  This allows more total flexibility and unlimited  measurements per segment.
N_MEASUREMENTS = 4 # Number of measurements to make per segment, an integer
MeasHeader = "VMin CH1 (V),Vpeak-peak CH3 (V),Frequency CH1 (Hz),Vavg Ch1 (V)" # Example Header = "M1 (units),M2 (units),M3 (units),..."
    ## Segment Index, Segment Time Tag (s) will automatically be added

## Save time tags to separate file?
SAVE_TTS_SEPARATELY = "YES" # "YES" or "N0" ; creates a separate file with only time tags and segment index
    ## Note that both saving waveform data and measurements will also save time tags in those files
    ## This can be used to get ONLY time tags.

## Save Locations
BASE_FILE_NAME = "my_data"
BASE_DIRECTORY = "C:\\Users\\Public\\"
    ## IMPORTANT NOTE:  This script WILL overwrite previously saved files!

##############################################################################################################################################################################
##############################################################################################################################################################################
## Main code
##############################################################################################################################################################################
##############################################################################################################################################################################

print "Script is running.  This may take a while..."

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

## DO NOT RESET THE SCOPE!

##############################################################################################################################################################################
##############################################################################################################################################################################
## Flip through segments, get time tags and make measurements
##############################################################################################################################################################################
##############################################################################################################################################################################

## Find number of segments actually acquired
NSEG = int(KsInfiniiVisionX.query(":WAVeform:SEGMented:COUNt?"))
## compare with :ACQuire:SEGMented:COUNt?
## :ACQuire:SEGMented:COUNt? is how many segments the scope was set to acquire
## :WAVeform:SEGMented:COUNt? is how many were actually acquired
## KEY POINT:
    ## Using fewer segments can result in a higher sample rate.
    ## If the user sets the scope to acquire the maximum number for segments, and STOPS it before it is done,
    ## it is likely that a higher sample rate could have been achieved.
print str(NSEG) + " segments were acquired."
if NSEG == 0:
    ## Close Connection to scope properly
    KsInfiniiVisionX.clear()
    KsInfiniiVisionX.close()
    sys.exit("No segments acquired, aborting script.")

## pre-allocate TimeTag data array
Tags =  np.zeros(NSEG)

## pre-allocate measurement data array
if DO_MEASUREMENTS == "YES":
    MeasData = np.zeros([NSEG,N_MEASUREMENTS+2])

## Flip through segments...
for n in range(1,NSEG+1,1): ## Python indices start at 0, segments start at 1

    KsInfiniiVisionX.write(":ACQuire:SEGMented:INDex " + str(n)) # Go to segment n

    Tags[n-1] = KsInfiniiVisionX.query(":WAVeform:SEGMented:TTAG?") # Get time tag of segment n ; always get time tags

    if DO_MEASUREMENTS == "YES": ## FLAG_DEFINE_MEASUREMENTS
    
        ## As an alternate method to the below method of explicitly defining each measurement, one could setup measurements on the scope,
            ## and just grab and parse the results with results = KsInfiniiVisionX.query(":MEASure:RESults?”).split(,).  Refer to programmer’s guide for more details.
            ## Also requires user to let the oscilloscope “analyze” the segments.
            ## However, the oscilloscope may not allow for more than so many measurements (up to 10, depending on oscilloscope), and using more than
            ## 1 custom threshold per channel does not work on the oscilloscope itself.  The below method has no such limitations.
    
        M1 = KsInfiniiVisionX.query(":MEASure:VMIN? CHANnel1") # With the question mark after the measurement, the scope makes a measurement and returns it, but it does not show up on screen
        M2 = KsInfiniiVisionX.query(":MEASure:VPP? CHANnel3")
        M3 = KsInfiniiVisionX.query(":MEASure:DEFine THResholds,ABSolute,2,1.15,0.25,CHANnel1;:MEASure:FREQuency? CHANnel1;:MEASure:DEFine THResholds,STANdard,CHANnel1") # shows how to change thresholds and make a measurement with them.
            ## Note the threshold definition code and measurement is split with a semi-colon ;
            ## IMPORTANT NOTE:
                ## When the loop starts over it will now have perhaps wrong thresholds for some other timing measurement on ch1 because of the above threshold definition.
                ## Thus, one may need to adjust/reset thresholds... for example: :MEASure:DEFine THResholds,STANdard,CHANnel1 is used (with a ;) to rese the thresholds

        ## This next line shows how to use the ZOOM WINDOW to gate a measurement
        M4 = KsInfiniiVisionX.query(":TIMebase:MODE WINDow;:TIMebase:WINDow:Range 20.00E-06;:TIMebase:WINDow:POSition -250E-06;:MEASure:WINDow ZOOM;:MEASure:VAVerage?;:MEASure:WINDow MAIN;:TIMebase:MODE MAIN")
        ## It is performed like this:
            ##  Note everything was concatenated with semi-colons, as this speeds things up
            ## 1. Turn on zoom window with :TIMebase:MODE WINDow
            ## 2. Adjust width and range (total width) and then position of zoom window with :TIMebase:WINDow:Range 20.00E-06 and :TIMebase:WINDow:POSition -250E-06
                ## Note, for the ZOOM window, a negative position moves the window to the left, which is opposite the MAIN window behavior
                ## Need to adjust width (RANGe) before the POSition as POSition can change when the RANGE is adjusted
            ## 3. Tell oscilloscope to apply measurements to Zoom window with :MEASure:WINDow ZOOM
            ## 4. Make measurement (adjust thresholds as needed)
            ## 5. Tell oscilloscope to go back to making measurements on main time window with :MEASure:WINDow MAIN
            ## 6. Turn off zoom window (really, turning of the zoom window takes care of step 5, but is left in for clarity and robustness) with :TIMebase:MODE MAIN
            ## On the X4000A, X3000T, and X6000A, it is possible to gate measurements with the cursors: use :MEASure:WINDow GATE instead of :MEASure:WINDow ZOOM, and setup the marker X1 and X2 positions
        
        ## Note: M3 and M4 are rather likely to cuase "Data out of Range Errors" for a generic setup...

        ## Add additional measurements here and modify Data and Header as needed
        ## M5 = KsInfiniiVisionX.query(":MEASure:VPP? CHANnel1")
    
        ## This next measurement shows how to do a delay measurement on 2 channels with custom threhsolds for each
        ## M6: = KsInfiniiVisionX.query(":MEASure:DEFine THResholds,ABSolute,2.6,1,0.3,CHANnel1;:MEASure:DEFine THResholds,ABSolute,2,0.5,.3,CHANnel3;:MEASure:DEFine DELay,3,-1;:MEASure:DELay? CHANNEL1,CHANNEL3;:MEASure:DEFine THResholds,STANdard,CHANnel1")
            ## Defines absolute upper, middle, then lower thershold voltages (in that order) on channels 1 and then different ones on channel 3
                ## :MEASure:DEFine THResholds,ABSolute,2.6,1,0.3,CHAN1
                ## :MEASure:DEFine THResholds,ABSolute,2,0.5,.3,CHAN2
            ## Defines the edges for the delay mesurement as the 3rd rising edge on the first channel, and the first falling edge on the second channel
                ## :MEASure:DEFine DELay,3,-1
                ## NOTE: If there is an edge close to the left side of the screen, it may not count it…. So do some tests first, of course
            ## Actually measure dealy with: :MEASure:DELay? CHANNEL1,CHANNEL3
            ## Reset thresholds... (reset delay definition if needed)

        ## Assign results to Data array
        MeasData[n-1,0] = n ## segment index
        MeasData[n-1,1] = Tags[n-1] ## segment time tag
        MeasData[n-1,2] = M1 ## first measurement
        MeasData[n-1,3] = M2 ## second measurement
        MeasData[n-1,4] = M3 ## third measurement
        MeasData[n-1,5] = M4 ## Fourth measurement
        ## Add more measurements to Data as needed
        ## MeasData[n-1,6] = M5 ## Fifth measurement

    if GET_WFM_DATA == "YES":
        if n == 1: # Only need to do some things once

            ## Determine which channels are on, and which have acquired data, and get the vertical pre-amble info accordingly
                ## Use brute force method for readability

            CHS_ON = [0,0,0,0] # Create empty array to store channel states
            NUMBER_CHANNELS_ON = 0

            ## Channel 1
            on_off = int(KsInfiniiVisionX.query(":CHANnel1:DISPlay?"))
            Channel_acquired = int(KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel1;:WAVeform:POIN?")) # If there are no points available
                ## this channel did not capture data and thus there are no points (but was turned on)
            if Channel_acquired == 0 or on_off == 0:
                KsInfiniiVisionX.write(":CHANnel1:DISPlay OFF") # Setting a channel to be a waveform source turns it on...
                CHS_ON[0] = 0
                Y_INCrement_Ch1 = "BLANK"
                Y_ORIGin_Ch1    = "BLANK"
                Y_REFerence_Ch1 = "BLANK"
            else:
                CHS_ON[0] = 1
                NUMBER_CHANNELS_ON += 1
                Pre = KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel1;:WAVeform:PREamble?").split(',')
                Y_INCrement_Ch1 = float(Pre[7]) # Voltage difference between data points
                Y_ORIGin_Ch1    = float(Pre[8]) # Voltage at center screen
                Y_REFerence_Ch1 = float(Pre[9]) # Specifies the data point where y-origin occurs, alwasy zero
                    ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.

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

            ANALOGVERTPRES = (Y_INCrement_Ch1, Y_INCrement_Ch2, Y_INCrement_Ch3, Y_INCrement_Ch4, Y_ORIGin_Ch1, Y_ORIGin_Ch2, Y_ORIGin_Ch3, Y_ORIGin_Ch4, Y_REFerence_Ch1, Y_REFerence_Ch2, Y_REFerence_Ch3, Y_REFerence_Ch4)
            del Pre, on_off, Channel_acquired

            ## Find first channel on
            ch = 1
            for each_value in CHS_ON:
                if each_value ==1:
                    FIRST_CHANNEL_ON = ch
                    break
                ch +=1
            del ch, each_value

            ## Setup data export
            KsInfiniiVisionX.write(":WAVeform:FORMat WORD")  # 16 bit word format...
            KsInfiniiVisionX.write(":WAVeform:BYTeorder LSBFirst") # Explicitly set this to avoid confusion
            KsInfiniiVisionX.write(":WAVeform:UNSigned 0") # Explicitly set this to avoid confusion
            KsInfiniiVisionX.write(":WAVeform:SOURce CHANnel" + str(FIRST_CHANNEL_ON))  # Set waveform source to any enabled channel, here the FIRST_CHANNEL_ON
            KsInfiniiVisionX.write(":WAVeform:POINts MAX") # Set number of points to max possible for any InfiniiVision; ensures all are available
                ## If using :WAVeform:POINts MAX, be sure to do this BEFORE setting the :WAVeform:POINts:MODE as it will switch it to MAX
            KsInfiniiVisionX.write(":WAVeform:POINts:MODE RAW")  # Set this now so when the preamble is queried it knows what how many points it can retrieve from
                ## If measurements are also being made, they are made on a different record, the "measurement record."  This record can be accessed by using:
                ## :WAVeform:POINts:MODE NORMal isntead of :WAVeform:POINts:MODE RAW
            POINTS = int(KsInfiniiVisionX.query(":WAVeform:POINts?")) # Get number of points.  This is the number of points in each segment.
            print str(POINTS) + " points were acquired for each channel for each segment."

            ## Get timing pre-amble data - this can be done at any segment - it does not change segment to segment
            Pre = KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',')
            AMODE        = float(Pre[1]) # Gives the scope acquisition mode
            X_INCrement = float(Pre[4]) # Time difference between data points
            X_ORIGin    = float(Pre[5]) # Always the first data point in memory
            X_REFerence = float(Pre[6]) # Specifies the data point associated with x-origin; The x-reference point is the first point displayed and XREFerence is always 0.
                ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.
            del Pre

            ## Pre-allocate data array
            if AMODE == 1: # This means peak detect mode
                Wav_Data = np.zeros([NUMBER_CHANNELS_ON,2*POINTS,NSEG])
                ## Peak detect mode returns twice as many points as the points query, one point each for LOW and HIGH values
            else: # For all other acquistion modes
                Wav_Data = np.zeros([NUMBER_CHANNELS_ON,POINTS,NSEG])

            ## Create time axis:
            DataTime = ((np.linspace(0,POINTS-1,POINTS)-X_REFerence)*X_INCrement)+X_ORIGin
            if AMODE == 1: # This means peak detect mode
                DataTime = np.repeat(DataTime,2)
                ##  The points come out as Low(time1),High(time1),Low(time2),High(time2)....

        ## Pull waveform data, scale it - for every segment
        ch = 1 # channel number
        i  = 0 # index of Wav_data
        for each_value in  CHS_ON:
            if each_value == 1:
                ## Gets the waveform in 16 bit WORD format
                Wav_Data[i,:,n-1] = np.array(KsInfiniiVisionX.query_binary_values(':WAVeform:SOURce CHANnel' + str(ch) + ';DATA?', "h", False))
                ## Scales the waveform
                Wav_Data[i,:,n-1] = ((Wav_Data[i,:,n-1]-ANALOGVERTPRES[ch+7])*ANALOGVERTPRES[ch-1])+ANALOGVERTPRES[ch+3]
                    ## For clarity: Scaled_waveform_Data[*] = [(Unscaled_Waveform_Data[*] - Y_reference) * Y_increment] + Y_origin
                i +=1
            ch +=1
        del ch, i,

## End of flipping through segments
## Some cleanup
if GET_WFM_DATA == "YES":
    del  ANALOGVERTPRES,Y_INCrement_Ch1, Y_ORIGin_Ch1, Y_REFerence_Ch1, Y_INCrement_Ch2, Y_ORIGin_Ch2, Y_REFerence_Ch2,Y_INCrement_Ch3, Y_ORIGin_Ch3, Y_REFerence_Ch3, Y_INCrement_Ch4, Y_ORIGin_Ch4, Y_REFerence_Ch4, X_INCrement, X_ORIGin, X_REFerence

## Close Connection to scope properly
KsInfiniiVisionX.clear()
KsInfiniiVisionX.close()

## Data save operations

if DO_MEASUREMENTS == "YES":
    ## Slightly rededifne measurement header info
    MeasHeader = "Segment Index, Segment Time Tag (s)," + MeasHeader

    ## Save measurement data in csv format - openable in Microsoft XL and most other software...
    filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Measurements.csv"
    with open(filename, 'w') as filehandle:
        filehandle.write(str(MeasHeader) + "\n")
        np.savetxt(filehandle, MeasData, delimiter=',')
    del filehandle, filename

## Save waveform data
if GET_WFM_DATA == "YES":

    if DO_AVERAGE == "YES":
        Ave_Data = np.mean(Wav_Data,axis = 2)
        Wav_Data = np.dstack((Wav_Data,Ave_Data))
        del Ave_Data

    segment_indices = np.linspace(1,NSEG,NSEG, dtype = int)

    ch = 1
    for each_value in CHS_ON:
        if each_value == 1:
            filename = BASE_DIRECTORY + BASE_FILE_NAME + "_Channel" + str(ch) + ".csv"
            with open(filename, 'w') as filehandle:
                filehandle.write("Timestamp (s):,")
                np.savetxt(filehandle, np.atleast_2d(Tags), delimiter=',')
                filehandle.write("Segment Index:,")
                np.savetxt(filehandle, np.atleast_2d(segment_indices), delimiter=',')
                if DO_AVERAGE == "YES":
                    filehandle.write("Time (s), Waveforms... Final column is averaged.\n")
                else:
                    filehandle.write("Time (s), Waveforms...\n")
                np.savetxt(filehandle, np.insert(Wav_Data[ch-1,:,:],0,DataTime,axis=1), delimiter=',')
            ch +=1
    del each_value, ch, filehandle, filename, segment_indices

if SAVE_TTS_SEPARATELY == "YES":
    segment_indices = np.linspace(1,NSEG,NSEG, dtype = int)
    TTs_v_Index = np.zeros([NSEG,2])
    TTs_v_Index[:,0] = np.atleast_2d(segment_indices)
    TTs_v_Index[:,1] = np.atleast_2d(Tags)

    filename = BASE_DIRECTORY + BASE_FILE_NAME + "_TimeTags.csv"
    with open(filename, 'w') as filehandle:
        filehandle.write("Segment Index,Timestamp (s)\n")
        np.savetxt(filehandle, TTs_v_Index, delimiter=',')
    del filehandle, filename, segment_indices

del n, BASE_DIRECTORY, BASE_FILE_NAME, MeasHeader

print "Done."