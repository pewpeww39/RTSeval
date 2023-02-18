from Test.driverTest import Keithley2600
#from keithley2600 import Keithley2600
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
picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\rtsData"

def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def clearSMU():
    smu.errorqueue.clear()
    smu.eventlog.clear()
    smu.smua.reset()
    smu.smub.reset()


aData = pd.DataFrame(data=[], index=[], columns=[]) 
bData = pd.DataFrame(data=[], index=[], columns=[])
rtsData = pd.DataFrame(data=[], index=[], columns=[]) 
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W', 'L', 'Type']) 
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
pico = serial.Serial('COM4', baudrate=115200)
clearSMU()
rowSelect = 1
rowNum = 1
rowS = "Row 1"
for c in range(rowNum):
    commandTX = write_cmd(str(4))                                                   # increments the column to test
    commandRX1 = pico.read_until().strip().decode()
    time.sleep(.5)
    print('pico confirmed: ' + str(commandRX1))
    column = write_cmd(str(rowSelect))
    rowRX = pico.read_until().strip().decode()
    print('pico selected row: ' + str(rowRX))
    commandRX = int(pico.read_until().strip().decode())
    if commandRX == 1:
        for i in range(5000):
            vOut = smu.sourceA_measAB(smu.smua, smu.smub, pow(10, -9), 60, .001, .001)
# aData['V1'] = v1
# aData['currIn'] = i1
            bData[rowS] = vOut
            rtsData = pd.concat([rtsData, bData], axis = 0, ignore_index=True)
            rtsData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/rtsLoopData.csv')
            bData = bData.drop(rowS, axis=1)
    # rtsData = pd.concat([rtsData, bData], axis = 1)
    plt.plot(rtsData, label = "Vs")
    plt.title("RTS Data: Column 1")
    plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
    plt.figtext(.2, .2, "Ibias = 1 nA, AmpBias = .5 mA", fontsize = 10)
    plt.figtext(.2, .25, "column = 1, row = " + str(rowNum), fontsize = 10)
    plt.xlabel("Time [mSec]")
    plt.ylabel("Voltage [V]")
    plt.legend()
    plt.savefig(picLoc + " " + str(rowS) + " "+ dt_string + " TS.png")
    fig1 = plt.show(block = False)
    plt.pause(3)
    plt.close(fig1)
    plt.hist(rtsData, label = "Vs")
    plt.title("RTS Data: Column 1")
    plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
    plt.figtext(.2, .2, "Ibias = 1 nA, AmpBias = .5 mA", fontsize = 10)
    plt.figtext(.2, .25, "column = 1, row = " + str(rowNum), fontsize = 10)
    plt.xlabel("Time [mSec]")
    plt.ylabel("Voltage [V]")
    plt.legend()
    plt.savefig(picLoc + " " + str(rowS) + dt_string + " " + " Hist.png")
    fig1 = plt.show(block = False)
    plt.pause(3)
    plt.close(fig1)
    # bData = bData.drop(rowS, axis=1)
    # rowSelect = rowSelect + 1
    # rowS = re.sub(r'[0-9]+$',
    #          lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
    #          rowS)

rtsData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/rtsData' + dt_string + '.csv')
# smu._write(value='smua.source.output = smua.OUTPUT_OFF')
# smu._write(value='smub.source.output = smub.OUTPUT_OFF')
# smu.eventlog.clear()