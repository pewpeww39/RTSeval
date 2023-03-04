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
rowSelect = 1
colSelect = 1
rowNum = 1
colNum = 32
rowS = "Row 1"
colS = "Col 1"
for c in range(rowNum):
    for c in range(colNum):
        commandTX = write_cmd(str(4))                                                   # selects the switch case on the pico
        commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
        time.sleep(.5)
        print('pico confirmed: ' + str(commandRX))
        write_cmd(str(rowSelect))                                              # increments the column to test
        rowRX = pico.read_until().strip().decode()                                   # confirms column selected
        print('pico selected row: ' + str(rowRX))
        time.sleep(.5)
        write_cmd(str(colSelect))                                              # increments the column to test
        columnRX = pico.read_until().strip().decode()                                   # confirms column selected
        print('pico selected column: ' + str(columnRX))
        time.sleep(.5)
        commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
        print('pico loaded shift register')
        spec = list(specData.iloc[c+1])
        if commandRX == 1:
            for i in range(1):
                smu._write(value = "smub.measure.autozero = smub.AUTOZERO_AUTO")
                smu.smub.measure.v()
                time.sleep(.5)
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
        plt.figtext(.2, .25, "column = " + str(colNum) + ", row = " + str(rowNum), fontsize = 10)
        plt.figtext(.2, .3, spec, fontsize = 10)
        plt.xlabel("Time [mSec]")
        plt.ylabel("Voltage [V]")
        plt.legend()
        plt.ylim(1.08, 1.12)
        plt.savefig(picLoc + " " + str(colS) + " " + str(rowS) + " "+ dt_string + " TS.png", dpi = 1000)
        fig1 = plt.show(block = False)
        plt.pause(3)
        plt.close(fig1)
        plt.hist(rtsData, label = "Vs", histtype="stepfilled", bins=100)
        plt.title("RTS Data: Column 1")
        plt.figtext(.2, .15, "Vgs = 0.17, Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
        plt.figtext(.2, .2, "Ibias = 5 nA, AmpBias = .5 mA", fontsize = 10)
        plt.figtext(.2, .25, "column = " + str(colNum) + ", row = " + str(rowNum), fontsize = 10)
        # plt.xlabel("Time [mSec]")
        plt.xlabel("Voltage [V]")
        plt.legend()
        plt.savefig(picLoc + " " + str(colS) + " " + str(rowS) + " " + dt_string + " " + " Hist.png")
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