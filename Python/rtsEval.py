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

dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\loopData\\rtsData"

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

def plotrts(fileLoc, row, rtsData):
    dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    plt.plot(rtsData['Row 1'], label='Vs')
    plt.title("RTS Data: Column 1")
    plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
    plt.figtext(.2, .2, "Ibias = 0.8 nA, AmpBias = .5 mA", fontsize = 10)
    plt.figtext(.2, .25, "column = 1, row = " , fontsize = 10)
    plt.xlabel("Time [mSec]")
    plt.ylabel("Voltage [V]")
    plt.legend()
    plt.savefig(fileLoc + " " + str(rowS) + " TS.png")
    fig1 = plt.show(block = False)
    # plt.pause(5)
    plt.close(fig1)
    plt.hist(rtsData['Row 1'], label = "Vs")
    plt.title("RTS Data: Column 1")
    plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
    plt.figtext(.2, .2, "Ibias = 0.8 nA, AmpBias = .5 mA", fontsize = 10)
    plt.figtext(.2, .25, "column = 1, row = " , fontsize = 10)
    # plt.xlabel("Time [mSec]")
    plt.xlabel("Voltage [V]")
    plt.legend()
    plt.savefig(fileLoc + " " + str(rowS) + " Hist.png")
    fig2 = plt.show(block = False)
    # plt.pause(5)
    plt.close(fig2)

def bankNum(bank):
    rowStart = 1
    rowEnd = 96 + 1 
    if bank == 1:
        colStart = 1
        colEnd = colStart + 32
        colS = "Col000"   
        rowS = "Row00"
        sweepList = np.append(np.linspace(0, 1.2), np.linspace(0, 1.2)) 
        vdListA = np.full(50, 0.1)
        vdListB = np.full(50, 0.8)
        vdList = np.append(vdListA, vdListB)
        csIn = 5
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 1\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 1/rtsData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 2:
        colStart = 33
        colEnd = colStart + 32
        colS = "Col032"   
        rowS = "Row00"
        sweepList = np.append(np.linspace(0, 1.2), np.linspace(0, 1.2)) 
        vdListA = np.full(50, 0.1)
        vdListB = np.full(50, 0.8)
        vdList = np.append(vdListA, vdListB)
        csIn = 5
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 2\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 2/rtsData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 3:
        colStart = 65
        colEnd = colStart + 32
        colS = "Col064"   
        rowS = "Row00"
        sweepList = np.append(np.linspace(0, 3.3), np.linspace(0, 3.3)) 
        vdListA = np.full(50, 0.1)
        vdListB = np.full(50, 1.5)
        vdList = np.append(vdListA, vdListB)
        csIn = 5
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 3\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 3/rtsData'
        limiti = 0.01
        rangei = pow(10, -2)
    elif bank == 4:
        colStart = 97
        colEnd = colStart + 32
        colS = "Col096"   
        rowS = "Row00"
        sweepList = np.append(np.linspace(0, 3.3), np.linspace(0, 3.3)) 
        vdListA = np.full(50, 0.1)
        vdListB = np.full(50, 1.5)
        vdList = np.append(vdListA, vdListB)
        csIn = 5
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 4\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 4/rtsData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 5:
        colStart = 129
        colEnd = colStart + 32
        colS = "Col128"   
        rowS = "Row00"
        # sweepList = np.linspace(1.2, 0)
        # vdList = [1.1, 0.4] 
        sweepList = np.append(np.linspace(1.2, 0), np.linspace(1.2, 0)) 
        vdListA = np.full(50, 1.1)
        vdListB = np.full(50, 0.4)
        vdList = np.append(vdListA, vdListB)
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 5\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 5/rtsData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 6:
        colStart = 161
        colEnd = colStart + 32
        colS = "Col160"   
        rowS = "Row00"
        sweepList = np.append(np.linspace(3.3, 0), np.linspace(3.3, 0)) 
        vdListA = np.full(50, 3.2)
        vdListB = np.full(50, 1.8)
        vdList = np.append(vdListA, vdListB)
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 6\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 6/rtsData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 7:
        colStart = 193
        colEnd = colStart + 32
        colS = "Col192"   
        rowS = "Row00"
        sweepList = np.append(np.linspace(3.3, 0), np.linspace(3.3, 0)) 
        vdListA = np.full(50, 3.2)
        vdListB = np.full(50, 1.8)
        vdList = np.append(vdListA, vdListB)
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 7\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 7/rtsData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 8:
        colStart = 225
        colEnd = colStart + 32
        colS = "Col224"   
        rowS = "Row00"
        sweepList = np.append(np.linspace(3.3, 0), np.linspace(3.3, 0)) 
        vdListA = np.full(50, 3.2)
        vdListB = np.full(50, 1.8)
        vdList = np.append(vdListA, vdListB)
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\Bank 8\\rtsData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/Bank 8/rtsData'
        limiti = 0.001
        rangei = pow(10, -3)
    return rowStart, rowEnd, colStart, colEnd, colS, rowS, sweepList, vdList, csIn, picLoc, fileLoc, limiti, rangei

def powerPico():                                                                    # Turns on the vPwr pins for pi pico
    write_cmd(str(7))                                                               # selects the switch case on the pico
    pico.read_until().strip().decode()                                              # confirms mode selected
    print('pico turned on the power') 
    time.sleep(2)




vOut = pd.DataFrame(data=[], index=[], columns=[]) 
bData = pd.DataFrame(data=[], index=[], columns=[])
RTSData = pd.DataFrame(data=[], index=[], columns=[])
rtsData = pd.DataFrame(data=[], index=[], columns=[]) 
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W', 'L', 'Type']) 
fileLoc ="~\miniconda3\envs\\testequ\RTSeval\Python\Data\\rtsData\\loopData\\rtsLoopData.csv"
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W', 'L', 'Type'])
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
pico = serial.Serial('COM4', baudrate=115200)
clearSMU()


rowStart, rowEnd, colStart, colEnd, colS, rowS, sweepList, vdList, csIn, picLoc, fileLoc, limiti, rangei = bankNum(1)        # selects the bank to test
colBegin = colS
smu.apply_voltage(smu.smua, 0.0)
smu.apply_voltage(smu.smub, 0.0)
powerPico()

dieX = '6p'
dieY = '3'

for row in range(rowStart, rowEnd):
    for col in range(colStart, colEnd):
        # start_total_time = time.time()
        commandTX = write_cmd(f"{csIn},{row},{col}")                                                   # selects the switch case on the pico
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
        for i in range(1):
            smu._write(value = "smub.measure.autozero = smub.AUTOZERO_AUTO")
            smu.smub.measure.v()
            vOut = smu.sourceA_measAB(smu.smua, smu.smub, 0.000000005, 20, .001, .0005)
            bData[rowS] = vOut
            rtsData = pd.concat([rtsData, bData], axis = 1, ignore_index=True)
            rtsData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/rtsLoopData.csv')
            # plotrts(picLoc, 0, rtsData)
            bData = bData.drop(bData.index) 
            bData[rowS] = []
                
        # rtsData = pd.concat([rtsData, bData], axis = 1)
        plt.plot(rtsData, label = "Vs")
        plt.title("RTS Data: Column 1")
        plt.figtext(.2, .15, "Vgs = 0.17, Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
        plt.figtext(.2, .2, "Ibias = 5 nA, AmpBias = .5 mA", fontsize = 10)
        plt.figtext(.2, .25, "column = " + str(col) + ", row = " + str(row), fontsize = 10)
        plt.figtext(.2, .3, spec, fontsize = 10)
        plt.xlabel("Time [mSec]")
        plt.ylabel("Voltage [V]")
        plt.legend()
        plt.ylim(1.08, 1.12)
        plt.savefig(picLoc + " " + str(col) + " " + str(row) + " "+ dt_string + " TS.png", dpi = 1000)
        fig1 = plt.show(block = False)
        plt.pause(3)
        plt.close(fig1)
        plt.hist(rtsData, label = "Vs", histtype="stepfilled", bins=100)
        plt.title("RTS Data: Column 1")
        plt.figtext(.2, .15, "Vgs = 0.17, Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
        plt.figtext(.2, .2, "Ibias = 5 nA, AmpBias = .5 mA", fontsize = 10)
        plt.figtext(.2, .25, "column = " + str(col) + ", row = " + str(row), fontsize = 10)
        # plt.xlabel("Time [mSec]")
        plt.xlabel("Voltage [V]")
        plt.legend()
        plt.savefig(picLoc + " " + str(col) + " " + str(row) + " " + dt_string + " " + " Hist.png")
        fig1 = plt.show(block = False)
        plt.pause(3)
        plt.close(fig1)
        colS = re.sub(r'[0-9]+$',
                 lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
                 colS)
        
    # bData = bData.drop(rowS, axis=1)
    # rowSelect = rowSelect + 1
    # rowS = re.sub(r'[0-9]+$',
    #          lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
    #          rowS)
commandTX = write_cmd(str(9))                                                   # selects the switch case on the pico
commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
print('pico confirmed: ' + str(commandRX) + ' and reset the shift registers')
rtsData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/rtsData' + dt_string + '.csv')
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
# smu.eventlog.clear()