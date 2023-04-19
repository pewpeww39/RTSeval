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
from scipy.signal import find_peaks
from scipy.signal import argrelextrema

smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
pico = serial.Serial('COM4', baudrate=115200)

def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def clearSMU():
    smu.errorqueue.clear()
    smu.eventlog.clear()
    smu.smua.reset()
    smu.smub.reset()

def inport(file, idex, head, col):
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

def bankNum(bank):
    rowStart = 6
    rowEnd = 6 + 1 
    if bank == 1:
        colStart = 1
        colEnd = colStart + 1 # 32
        Ibias = 10e-6
        timeTest = 20
        holdTime = 20
        # timeDelay = 0.001         # 1 kHz
        # nplc = 0.05 / 60
        timeDelay = 0.0005          # 2 kHz
        nplc = 0.027 / 60
        csIn = 3
        sampRate = 1 / (timeDelay * 1000)
        # picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 1\\rtsData_Ibias_" + str(Ibias) 
        picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\rtsData\\Bank 1\\rtsData_Ibias_" + str(Ibias)
        fileLoc = '~/Documents/SkywaterData/rtsData/Bank 1/rtsData'
        limitv = 3.3
        rangev = 4
        
    elif bank == 2:
        # colStart = 33
        # colEnd = colStart + 32
        colStart = 1
        colEnd = colStart + 1
        # colS = "Col00" # "Col032"
        # rowS = "Row00"
        Ibias = 5e-9 
        timeTest = 1
        holdTime = 10
        timeDelay = 0.0001
        nplc = 0.001 / 60
        csIn = 3
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 2\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 2/rtsData'
        limitv = 3.3
        rangev = 4
    elif bank == 3:
        colStart = 65
        colEnd = colStart + 32
        colS = "Col064"   
        rowS = "Row00"
        Ibias = np.append(np.linspace(0, 3.3), np.linspace(0, 3.3)) 
        vdListA = np.full(50, 0.1)
        vdListB = np.full(50, 1.5)
        vdList = np.append(vdListA, vdListB)
        csIn = 3
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 3\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 3/rtsData'
        limitv = 3.3
        rangev = 4
    elif bank == 4:
        colStart = 97
        colEnd = colStart + 32
        colS = "Col096"   
        rowS = "Row00"
        Ibias = np.append(np.linspace(0, 3.3), np.linspace(0, 3.3)) 
        vdListA = np.full(50, 0.1)
        vdListB = np.full(50, 1.5)
        vdList = np.append(vdListA, vdListB)
        csIn = 3
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 4\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 4/rtsData'
        limitv = 3.3
        rangev = 4
    elif bank == 5:
        colStart = 129
        colEnd = colStart + 32
        colS = "Col128"   
        rowS = "Row00"
        # Ibias = np.linspace(1.2, 0)
        # vdList = [1.1, 0.4] 
        Ibias = np.append(np.linspace(1.2, 0), np.linspace(1.2, 0)) 
        vdListA = np.full(50, 1.1)
        vdListB = np.full(50, 0.4)
        vdList = np.append(vdListA, vdListB)
        csIn = 4
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 5\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 5/rtsData'
        limitv = 3.3
        rangev = 4
    elif bank == 6:
        colStart = 161
        colEnd = colStart + 32
        colS = "Col160"   
        rowS = "Row00"
        Ibias = np.append(np.linspace(3.3, 0), np.linspace(3.3, 0)) 
        vdListA = np.full(50, 3.2)
        vdListB = np.full(50, 1.8)
        vdList = np.append(vdListA, vdListB)
        csIn = 4
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 6\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 6/rtsData'
        limitv = 3.3
        rangev = 4
    elif bank == 7:
        colStart = 193
        colEnd = colStart + 32
        colS = "Col192"   
        rowS = "Row00"
        Ibias = np.append(np.linspace(3.3, 0), np.linspace(3.3, 0)) 
        vdListA = np.full(50, 3.2)
        vdListB = np.full(50, 1.8)
        vdList = np.append(vdListA, vdListB)
        csIn = 4
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 7\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 7/rtsData'
        limitv = 3.3
        rangev = 4
    elif bank == 8:
        colStart = 225
        colEnd = colStart + 32
        colS = "Col224"   
        rowS = "Row00"
        Ibias = np.append(np.linspace(3.3, 0), np.linspace(3.3, 0)) 
        vdListA = np.full(50, 3.2)
        vdListB = np.full(50, 1.8)
        vdList = np.append(vdListA, vdListB)
        csIn = 4
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 8\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 8/rtsData'
        limitv = 3.3
        rangev = 4
    return rowStart, rowEnd, colStart, colEnd, Ibias, timeDelay, nplc, timeTest, holdTime, csIn, picLoc, fileLoc, limitv, rangev, sampRate

def rtsMeasurement (bank, dieX, dieY):
    clearSMU()
     
    rtsData = pd.DataFrame(data=[], index=[], columns=[]) 
    specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W/L', 'Type'])
    rowStart, rowEnd, colStart, colEnd, Ibias, timeDelay, nplc, timeTest, holdTime, csIn, picLoc, fileLoc, limitv, rangev, sampRate = bankNum(bank)
    # colBegin = colS
    powerPico()  
    for row in range(rowStart, rowEnd):
        for col in range(colStart, colEnd):
            vOut = pd.DataFrame(data=[], index=[], columns=[])
            # start_total_time = time.time()
            write_cmd(f"{csIn},{row},{col}")                                                   # selects the switch case on the pico
            commandRX = tuple(pico.read_until().strip().decode().split(','))
            commandRX, rowRX, columnRX = commandRX
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
            smu.smub.measure.i()
            smu.apply_current(smu.smua, Ibias)
            time.sleep(holdTime)
            vOut['Vs'] = smu.sourceA_measAB(smu.smua, smu.smub, Ibias, timeTest, holdTime, timeDelay, nplc, limitv, rangev)
            vOut['Vgs'] = np.full_like(vOut['Vs'], 1.2) - vOut['Vs']
            vOut['Ticks'] = np.linspace(0, timeTest, len(vOut['Vs'])) 
            vOut['Column'] = col 
            vOut['Row'] = row 
            vOut['W/L'] = spec[0] 
            vOut['Type'] = spec[1] 
            vOut['DieX'] = dieX
            vOut['DieY'] = dieY
            print(len(vOut))
            rtsData = pd.concat([rtsData, vOut], axis = 0, ignore_index=True)
            rtsData.to_csv(fileLoc + '_Loop.csv')
            plt.figure(figsize=(12,8))
            plt.subplot(2,1,1)
            plt.plot(vOut.loc[900:, ['Ticks']], vOut.loc[900:, ['Vgs']], label = "Vgs")
            plt.title("RTS Data: " + str(spec[0]) + " " + str(spec[1]))
            plt.xlabel("Time (sec)")
            plt.ylabel("Vgs [V]")
            plt.legend()
            plt.subplot(2,1,2)
            x,y,_ = plt.hist(vOut['Vgs'], label = "Vgs", histtype="stepfilled", bins=50)
            peaks = argrelextrema(y, np.greater)
            # peaks, _ = find_peaks(y, distance=25)
            # # i_maxPeaks = peaks[np.argmax(y[peaks])]
            # xMax = x[peaks]
            print(y)
            rtsAmplitude = .000305 #np.round(xMax[1]-xMax[0], 6)
            plt.ylabel("Count")
            plt.xlabel("Vgs [V]")
            plt.legend()
            plt.figtext(.5, .95, "Vg = 1.2 V, Vdd = 1.2 V, Samp Rate = " + str(sampRate) + " kHz, Ibias = " + str(Ibias) + ' A' + 'RTS Amplitude = ' + str(rtsAmplitude), 
                        horizontalalignment='center', fontsize = 10)
            plt.savefig(picLoc + "_C" + columnRX + "R" + rowRX + " " + dt_string + ".png")
            fig1 = plt.show(block = False)
            plt.pause(3)
            plt.close(fig1)
            vOut = vOut.reset_index(drop = True, inplace=True)
            smu._write(value='smua.source.output = smua.OUTPUT_OFF')
            smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    write_cmd(str(9))                                                   # selects the switch case on the pico
    commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
    print('pico reset the shift registers')
    rtsData.to_csv(fileLoc + dt_string + '.csv')
    return rtsData


# for i in range(2):
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
rtsMeasurement(1, '5L', '3')
