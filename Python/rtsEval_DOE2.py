from keithleyDriver import Keithley2600
import numpy as np
import math
import time
import pandas as pd
from datetime import datetime
from os import system, name
import serial
import matplotlib.pyplot as plt
import re
from scipy.signal import find_peaks, savgol_filter, peak_widths
from scipy.signal import argrelmax, welch
import pyvisa
rm = pyvisa.ResourceManager()
picoCom = 'COM3'
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               # set ip addr for smu
smu2 = Keithley2600('TCPIP0::192.168.4.12::INSTR')               # set ip addr for smu
pico = serial.Serial('COM3', baudrate=115200)                   # set com port for pico com4 is old pico
powerSupply = rm.open_resource('TCPIP0::192.168.4.3::INSTR')
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub

def write_cmd(x):                                               # sends commands to pico
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def clearSMU():
    smu.errorqueue.clear()
    smu.eventlog.clear()
    smu.smua.reset()
    smu.smub.reset()

def inport(file, idex, head, col):                              # inport csv to dataframe
    df = pd.DataFrame(pd.read_csv(file, index_col=[idex] , header=head), 
                            columns = col)
    return df

def powerPico():                                                                    # Turns on the vPwr pins for pi pico
    write_cmd(str(7))                                                               # selects the switch case on the pico
    pico.read_until().strip().decode()                                              # confirms mode selected
    print('pico turned on the power') 
    time.sleep(2)

def powerSupply_Set(channel, voltage, current):
    powerSupply.write("INST "+channel) # Select +6V output ch 1
    powerSupply.write("VOLT "+voltage) # Set output voltage to 3.0 V
    powerSupply.write("CURR "+current) # Set output current to 1.0 A

def powerSupply_On():
    powerSupply.write("OUTP ON")

def powerSupply_Off():
    powerSupply.write("INST P6V")
    powerSupply.write("OUTP OFF")
    powerSupply.write("INST P25V")
    powerSupply.write("OUTP OFF")
    powerSupply.write("INST N25V")
    powerSupply.write("OUTP OFF")

debug = False

def bankNum(bank, bypass):
    rowStart = 0 + 1
    rowEnd = rowStart + 1 

    if bypass is True and bank in [0,1,2,3]:
        select = 3
    elif bypass is False and bank in [0,1,2,3]:
        select = 3
    elif bypass is True and bank in [4,5,6,7]:
        select = 6
    elif bypass is False and bank in [4,5,6,7]:
        select = 4
    else:
        print('Bypass not selected')
        select = 0

    if bank == 0:
        colStart = 0 + 1 
        # colEnd = colStart + 16
        colEnd = colStart + 1
        Iref = -1e-5
        timeTest = 4
        holdTime = 2
        # timeDelay = 0.001                             # 1 kHz
        # nplc = 0.05 / 60
        timeDelay = 0.0005          # measure delay     # 2 kHz
        nplc = 0.027 / 60           # integration time
        csIn = select                     # pico command
        sampRate = 1 / (timeDelay * 1000)
        # picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 1\\rtsData_Iref_" + str(Iref) 
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\rtsData\\Bank 0\\rtsData_Iref_" + str(Iref)
        fileLoc = '~/Documents/SkywaterData/DOE2/rtsData/Bank 0/rtsData'
        limitv = 3.3
        rangev = 2
        vg = 3.3
    elif bank == 1:
        # colStart = desired column + 1
        colStart = 16+1
        colEnd = colStart + 16
        Iref = -10e-9
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 1\\rtsData_Iref_" + str(Iref)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 1/rtsData'
        limitv = 3.3
        rangev = 2
        vg = 1.2
    elif bank == 2:
        colStart = 32 + 1
        colEnd = colStart + 16
        Iref = -1e-5
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 2\\rtsData_Iref_" + str(Iref)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 2/rtsData'
        limitv = 3.3
        rangev = 3.3
        vg = 3.3
    elif bank == 3:
        colStart = 48 + 1
        colEnd = colStart + 16
        Iref = -1e-7
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 3\\rtsData_Iref_" + str(Iref)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 3/rtsData'
        limitv = 3.3
        rangev = 3.3
        vg = 3.3
    elif bank == 4:
        colStart = 64 + 1
        colEnd = colStart + 16
        Iref = -1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 4\\rtsData_Iref_" + str(Iref)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 4/rtsData'
        limitv = 3.3
        rangev = 1
        vg = 1.2
    elif bank == 5:
        colStart = 80 + 1
        colEnd = colStart + 16
        Iref = -1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 5\\rtsData_Iref_" + str(Iref)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 5/rtsData'
        limitv = 3.3
        rangev = 1
        vg = 3.3
    elif bank == 6:
        colStart = 96 + 1
        colEnd = colStart + 16
        Iref = -1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 6\\rtsData_Iref_" + str(Iref)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 6/rtsData'
        limitv = 3.3
        rangev = 1
        vg = 3.3
    elif bank == 7:
        colStart = 112 + 1
        colEnd = colStart + 16
        Iref = -1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 7\\rtsData_Iref_" + str(Iref)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 7/rtsData'
        limitv = 3.3
        rangev = 1
        vg = 3.3
    return rowStart, rowEnd, colStart, colEnd, Iref, timeDelay, nplc, timeTest, holdTime, csIn, picLoc, fileLoc, limitv, rangev, sampRate, vg

def rtsMeasurement (bank, dieX, dieY, bypass):
    clearSMU()
     
    rtsData = pd.DataFrame(data=[], index=[], columns=[]) 
    # specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
    #                  index_col=[0] , header=0), columns = ['W/L', 'Type'])
    rowStart, rowEnd, colStart, colEnd, Iref, timeDelay, nplc, timeTest, holdTime, csIn, picLoc, fileLoc, limitv, rangev, sampRate, vg = bankNum(bank, bypass)


    powerSupply_Set("P25V", "5.333", "1.0")
    powerSupply_On()
    powerPico()  

    RTSCounter = 0                                                                # Counter variable for RTS detection(Jay Kim 06/06/23 9:04PM)
    SlowTrapCounter = 0                                                           # Counter variable for SlowTrapRTS detection(Jay Kim 06/06/23 9:04PM)
    DeviceCounter = 0                                                             # Counter variable for Device Counter(Jay Kim 06/06/23 9:04PM)
    for row in range(rowStart, rowEnd):
        for col in range(colStart, colEnd):
            DeviceCounter += 1                                                    #Device Counter
            print('Device Count:', DeviceCounter)
            vOut = pd.DataFrame(data=[], index=[], columns=[])
            # start_total_time = time.time()
            write_cmd(f"{csIn},{row},{col}")                                                   # selects the switch case on the pico
            commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))
            # end_command_time = time.time()
            rowRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                    rowRX)  
            columnRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the colimn number
                    columnRX)    
            print('pico confirmed: ' + str(commandRX))
            print('pico selected row: ' + str(rowRX))
            print('pico selected column: ' + str(columnRX))
            # start_response_time = time.time()
            commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
            print(f'pico loaded the shift registers')                           # confirms shift registers are loaded
            # end_response_time = time.time()
            # start_voltage_sweep = time.time()
            # spec = list(specData.iloc[col - 1])
            smu._write(value = "smua.measure.autozero = smua.AUTOZERO_AUTO")
            smu._write(value='smua.source.output = smub.OUTPUT_ON')
            smu.smua.measure.v()
            smu.apply_current(smu.smub, Iref)
            smu2.apply_current(smu2.smua, 0.0)
            time.sleep(holdTime)
            print("Starting Test")
            write_cmd(f"{5}")  
            vOut['V_C Out'] = smu.sourceA_measAB(smu.smub, smu.smua, Iref, timeTest, holdTime, timeDelay, nplc, rangev, limitv)     # run the script on smu
            vOut['Vsg'] = np.full_like(vOut['V_C Out'], vg) - vOut['V_C Out']
            vOut['Id'] = Iref/10
            vOut['Sample_Rate(kHz)'] = sampRate
            vOut['Ticks'] = np.linspace(0, timeTest, len(vOut['V_C Out'])) 
            vOut['Column'] = columnRX
            vOut['Row'] = rowRX
            # vOut['W_L'] = spec[0] 
            # vOut['Type'] = spec[1] 
            vOut['DieX'] = dieX
            vOut['DieY'] = dieY
            print(len(vOut))
            rtsData = pd.concat([rtsData, vOut], axis = 0, ignore_index=True)           # save the new data with old data
            sig = savgol_filter(vOut["V_C Out"], window_length=51, polyorder=3)
            y1, x1 = np.histogram(sig, bins=50)
            peak = find_peaks(y1, width=1, height=100, distance=5)
            YMAX = y1[peak[0]]
            XMAX = x1[peak[0]]
            if len(peak[0]) >= 2:
                SlowTrapCounter += 1                                 
                for k in range(0, len(peak[0])):
                    if y1[peak[0][k]] == max(YMAX):
                        steadystate = k
                rtsAmplitude = x1[peak[0]] - x1[peak[0][steadystate]]
                rtsAmplitude = rtsAmplitude[rtsAmplitude != 0.]
                peaks, _ = find_peaks(sig, width=5, prominence=np.abs(min(rtsAmplitude)),      # find peaks of the filtered signal
                                   rel_height=0.5)
                peaks2, _ = find_peaks(-sig, width=5, prominence=np.abs(min(rtsAmplitude)))    # find peaks of the negative filtered signal

                results_W, results_WH, results_ips, results_rps= peak_widths(sig,           # find the peak widths (capture time)
                                                                            peaks, rel_height=0.5)
                results_NW, results_NWH, results_Nips, results_Nrps = peak_widths(-sig,     # find the valley widths (emission time)
                                                                                peaks2, rel_height=0.5)
                
                                                                                            # capture and emission maybe flipped depending on signal
            else: 
                peaks = []

            if len(peaks) >= 2:
                # print(xMax, ' ', yMax)
                # rtsAmplitude = np.round(xMax[1]-xMax[0], 6)
                RTSCounter += 1                                                             #RTS Counter
                plt.figure(figsize=(12,14))
                plt.subplot(3, 1, 1)
                if debug is False:
                    plt.plot(vOut['Ticks'], vOut['V_C Out'], label = "$V_{sg}$")
                    plt.plot(vOut.Ticks, sig, label = "Filterd Signal")
                    plt.xlabel("Time (sec)")
                else:
                    plt.plot(vOut['Vsg'], lbel='Vsg')
                    plt.plot(sig, label='Filtered Signal')
                    plt.plot(peaks, sig[peaks], 'x', color='red')
                    plt.plot(peaks2, sig[peaks2], 'x', color='green')
                    plt.hlines(results_WH, results_ips, results_rps, color="C2")
                    plt.xlabel('Data Points')
                plt.title("RTS Data: Col: " + str(col) + " Row: " + str(row)) # spec[0]) + " " + str(spec[1]))
                plt.ylabel("$V_{sg}$ [V]")
                plt.legend()

                plt.subplot(3,2,3)

                frq, P1d = welch(vOut.Vsg, fs=2000, window='hann', nperseg=20000,               #  Compute PSD using welch method
                                noverlap=None, nfft=20000)
                p1dSmooth = savgol_filter(P1d, window_length=5, polyorder=1)

                plt.yscale('log')
                plt.title('1/f Noise')
                plt.ylabel('$S_{id}$' + '($V^2$/Hz)')
                plt.xlabel("Frequency (Hz)")
                plt.xscale('log')
                plt.plot(frq[5:], P1d[5:])
                plt.plot(frq[5:], p1dSmooth[5:])

                # plt.subplot(2,1,2)
                plt.subplot(3, 2, 4)    
                plt.hist(vOut['Vsg'], label = "$V_{sg}$", histtype="stepfilled", bins=50)
                plt.hist(sig, label = 'Filtered Signal', histtype="stepfilled", bins=50)
                # plt.plot(xMax, yMax, 'x')
                plt.plot(XMAX, YMAX, 'o')
                plt.ylabel("Frequency")
                plt.xlabel("$V_{sg}$ [V]")
                plt.title('RTS Amplitude = ' + str(rtsAmplitude) + ' (V)')
                plt.legend()

                plt.subplot(3, 2, 5)
                plt.hist(results_W/2000, bins=50)
                meanTauE = np.mean(results_W)/2000
                plt.xlabel('Time (Sec)')
                plt.ylabel('Frequency')
                plt.title('Mean emission time: ' + str(meanTauE))

                plt.subplot(3, 2, 6)
                plt.hist((results_NW)/2000, bins=50)
                meanTauC = np.mean(results_NW)/2000
                plt.xlabel('Time (Sec)')
                plt.ylabel('Frequency')
                plt.title('Mean capture time: ' + str(meanTauC))
                
                plt.figtext(.5, .95, "$V_{g}$ = " + str(vg) +" V, $V_{dd}$ = "+ str(vg) + " V, Samp Rate = " + str(sampRate) + " kHz, $I_{ds}$ = " + str(Iref) +
                            ' A', horizontalalignment='center', fontsize = 10)
                plt.savefig(picLoc + "_C" + columnRX + "R" + rowRX + " " + dt_string + ".png")
                plt.tight_layout()
                fig1 = plt.show(block = False)
                # plt.pause(.5)
                plt.close(fig1)
            # else:
            #     rtsAmplitude = "???"
            
            vOut = vOut.reset_index(drop = True, inplace=True)
            smu._write(value='smua.source.output = smua.OUTPUT_OFF')
            smu._write(value='smub.source.output = smub.OUTPUT_OFF')
        rtsData.to_csv(fileLoc + '_Loop'+ rowRX + '.csv')                                   # save after row completes
        # rtsData.to_feather(fileLoc + '_Row'+ rowRX + '.feather')   
        rtsData = rtsData.reset_index(drop=True, inplace=True)                              # delete data frame after row completes
    write_cmd(str(9))                                                   # selects the switch case on the pico
    commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
    print('pico reset the shift registers')
    # rtsData.to_csv(fileLoc + dt_string + '.csv')
    print('Slow Trap Count:', SlowTrapCounter)
    print('RTS Count:', RTSCounter)
    totalRTS = SlowTrapCounter/DeviceCounter *100
    refinedRTS = RTSCounter/DeviceCounter *100
    print('totalRTS: ', totalRTS)
    print('refinedRTS: ', refinedRTS)
    return rtsData


# for i in range(2):
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
# rtsMeasurement(0, '5L', '3', bypass=True)                                  # (bank number, dieX, dieY, bypass select)
rtsMeasurement(0, '2E', '6', bypass=True)                                    #New Chip currently being measured
