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
from scipy.signal import find_peaks, savgol_filter
from scipy.signal import argrelmax

smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               # set ip addr for smu
pico = serial.Serial('COM4', baudrate=115200)                   # set com port for pico

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

# def plotrts(fileLoc, row, rtsData):
#     dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
#     plt.plot(rtsData['Row 1'], label='Vs')
#     plt.title("RTS Data: Column 1")
#     plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
#     plt.figtext(.2, .2, "Ibias = 0.8 nA, AmpBias = .5 mA", fontsize = 10)
#     plt.figtext(.2, .25, "column = 1, row = " , fontsize = 10)
#     plt.xlabel("Time [mSec]")
#     plt.ylabel("Voltage [V]")
#     plt.legend()
#     plt.savefig(fileLoc + " " + str(rowS) + " TS.png")
#     fig1 = plt.show(block = False)
#     # plt.pause(5)
#     plt.close(fig1)
#     plt.hist(rtsData['Row 1'], label = "Vs")
#     plt.title("RTS Data: Column 1")
#     plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
#     plt.figtext(.2, .2, "Ibias = 0.8 nA, AmpBias = .5 mA", fontsize = 10)
#     plt.figtext(.2, .25, "column = 1, row = " , fontsize = 10)
#     # plt.xlabel("Time [mSec]")
#     plt.xlabel("Voltage [V]")
#     plt.legend()
#     plt.savefig(fileLoc + " " + str(rowS) + " Hist.png")
#     fig2 = plt.show(block = False)
#     # plt.pause(5)
#     plt.close(fig2)

def bankNum(bank, bypass):
    rowStart = 0 + 1
    rowEnd = 96 + 1 

    if bypass is True and bank in [0,1,2,3]:
        select = 5
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
        colEnd = colStart + 32
        Ibias = 1e-8
        timeTest = 20
        holdTime = 20
        # timeDelay = 0.001                             # 1 kHz
        # nplc = 0.05 / 60
        timeDelay = 0.0005          # measure delay     # 2 kHz
        nplc = 0.027 / 60           # integration time
        csIn = select                     # pico command
        sampRate = 1 / (timeDelay * 1000)
        # picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 1\\rtsData_Ibias_" + str(Ibias) 
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 0\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 0/rtsData'
        limitv = 3.3
        rangev = 2
        vg = 1.2
    elif bank == 1:
        # colStart = desired column + 1
        colStart = 32+1
        colEnd = colStart + 32
        Ibias = 10e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 1\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 1/rtsData'
        limitv = 3.3
        rangev = 2
        vg = 1.2
    elif bank == 2:
        colStart = 64 + 1
        colEnd = colStart + 32
        Ibias = 1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 2\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 2/rtsData'
        limitv = 3.3
        rangev = 3.3
        vg = 3.3
    elif bank == 3:
        colStart = 97
        colEnd = colStart + 32
        Ibias = 22e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 3\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 3/rtsData'
        limitv = 3.3
        rangev = 4
        vg = 3.3
    elif bank == 4:
        colStart = 129
        colEnd = colStart + 32
        Ibias = 1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 4\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 4/rtsData'
        limitv = 3.3
        rangev = 1
        vg = 1.2
    elif bank == 5:
        colStart = 161
        colEnd = colStart + 32
        Ibias = 1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 5\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 5/rtsData'
        limitv = 3.3
        rangev = 1
        vg = 3.3
    elif bank == 6:
        colStart = 193
        colEnd = colStart + 32
        Ibias = 1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 6\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 6/rtsData'
        limitv = 3.3
        rangev = 1
        vg = 3.3
    elif bank == 7:
        colStart = 225
        colEnd = colStart + 32
        Ibias = 1e-6
        timeTest = 20
        holdTime = 20
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = select
        sampRate = 1 / (timeDelay * 1000)
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 7\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 7/rtsData'
        limitv = 3.3
        rangev = 1
        vg = 3.3
    return rowStart, rowEnd, colStart, colEnd, Ibias, timeDelay, nplc, timeTest, holdTime, csIn, picLoc, fileLoc, limitv, rangev, sampRate, vg

def rtsMeasurement (bank, dieX, dieY, bypass):
    clearSMU()
     
    rtsData = pd.DataFrame(data=[], index=[], columns=[]) 
    specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W/L', 'Type'])
    rowStart, rowEnd, colStart, colEnd, Ibias, timeDelay, nplc, timeTest, holdTime, csIn, picLoc, fileLoc, limitv, rangev, sampRate, vg = bankNum(bank, bypass)

    powerPico()  
    # saveCounter = 0
    for row in range(rowStart, rowEnd):
        for col in range(colStart, colEnd):
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
            spec = list(specData.iloc[col - 1])
            smu._write(value = "smub.measure.autozero = smub.AUTOZERO_AUTO")
            smu.smub.measure.v()
            smu.apply_current(smu.smua, Ibias)
            time.sleep(holdTime)
            vOut['Vs'] = smu.sourceA_measAB(smu.smua, smu.smub, Ibias, timeTest, holdTime, timeDelay, nplc, rangev, limitv)     # run the script on smu
            vOut['Vgs'] = np.full_like(vOut['Vs'], vg) - vOut['Vs']
            vOut['Ids'] = Ibias
            vOut['Sample_Rate(kHz)'] = sampRate
            vOut['Ticks'] = np.linspace(0, timeTest, len(vOut['Vs'])) 
            vOut['Column'] = columnRX
            vOut['Row'] = rowRX
            vOut['W_L'] = spec[0] 
            vOut['Type'] = spec[1] 
            vOut['DieX'] = dieX
            vOut['DieY'] = dieY
            print(len(vOut))
            rtsData = pd.concat([rtsData, vOut], axis = 0, ignore_index=True)           # save the new data with old data
            sig = savgol_filter(vOut.Vgs, window_length=51, polyorder=3)
            y1, x1 = np.histogram(sig, bins=50)
            y,x = np.histogram(vOut['Vgs'], bins=50)
            # peaks = argrelmax(y, order = 4)
            peaks = find_peaks(y, distance=5, width=2, height=100)
            peak = find_peaks(y1, width=1, height=100)
            yMax = y[peaks[0]]
            xMax = x[peaks[0]]
            YMAX = y1[peak[0]]
            XMAX = x1[peak[0]]
            if len(peak[0]) >= 2:                
                for k in range(0, len(peak[0])):
                    if y1[peak[0][k]] == max(YMAX):
                        steadystate = k
                rtsAmplitude = x1[peak[0]] - x1[peak[0][steadystate]]
                rtsAmplitude = rtsAmplitude[rtsAmplitude != 0.]
                # print(xMax, ' ', yMax)
                # rtsAmplitude = np.round(xMax[1]-xMax[0], 6)
                plt.figure(figsize=(12,8))
                plt.subplot(2,1,1)
                plt.plot(vOut['Ticks'], vOut['Vgs'], label = "Vgs")
                plt.plot(vOut.Ticks, sig, label = "Filterd Signal")
                plt.title("RTS Data: " + str(spec[0]) + " " + str(spec[1]))
                plt.xlabel("Time (sec)")
                plt.ylabel("Vgs [V]")
                plt.legend()
                plt.subplot(2,1,2)
                plt.hist(vOut['Vgs'], label = "Vgs", histtype="stepfilled", bins=50)
                plt.hist(sig, label = 'Filtered Signal', histtype="stepfilled", bins=50)
                # plt.plot(xMax, yMax, 'x')
                plt.plot(XMAX, YMAX, 'o')
                plt.ylabel("Count")
                plt.xlabel("Vgs [V]")
                plt.legend()
                
                plt.figtext(.5, .95, "Vg = " + str(vg) +" V, Vdd = "+ str(vg) + " V, Samp Rate = " + str(sampRate) + " kHz, Ibias = " + str(Ibias) +
                            ' A, Rts Amplitude = ' + str(rtsAmplitude) + ' (V)', horizontalalignment='center', fontsize = 10)
                plt.savefig(picLoc + "_C" + columnRX + "R" + rowRX + " " + dt_string + ".png")
                fig1 = plt.show(block = False)
                # plt.pause(.5)
                plt.close(fig1)
            # else:
            #     rtsAmplitude = "???"
            
            vOut = vOut.reset_index(drop = True, inplace=True)
            smu._write(value='smua.source.output = smua.OUTPUT_OFF')
            smu._write(value='smub.source.output = smub.OUTPUT_OFF')
        # rtsData.to_csv(fileLoc + '_Loop'+ rowRX + '.csv')                                   # save after row completes
        rtsData.to_feather(fileLoc + '_Row'+ rowRX + '.feather')   
        rtsData = rtsData.reset_index(drop=True, inplace=True)                              # delete data frame after row completes
    write_cmd(str(9))                                                   # selects the switch case on the pico
    commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
    print('pico reset the shift registers')
    # rtsData.to_csv(fileLoc + dt_string + '.csv')
    return rtsData


# for i in range(2):
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
rtsMeasurement(2, '5L', '3', bypass=True)                                  # (bank number, dieX, dieY, bypass select)
