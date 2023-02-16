from driverTest import Keithley2600
#from keithley2600 import Keithley2600
import numpy as np
import math
import time
import pandas as pd
from datetime import datetime
from os import system, name
import serial
import matplotlib.pyplot as plt

dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
picLoc = "C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\rtsData"

def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def logScale():
    decade1 = range(1,10, 1)
    decade2 = range(10,100, 10)
    decade3 = range(100,1000, 100)
    decade4 = range(1000,10000, 1000)
    decade5 = range(10000,100000, 10000)    
    decade6 = range(100000,1000000, 100000)
    decade7 = range(1000000,10000000, 1000000)
    decade8 = range(10000000,60000000, 10000000)
    decadeList = np.append(decade1, decade2)
    decadeList = np.append(decadeList, decade3)
    decadeList = np.append(decadeList, decade4)
    decadeList = np.append(decadeList, decade5)
    decadeList = np.append(decadeList, decade6)
    decadeList = np.append(decadeList, decade7)
    decadeList = np.append(decadeList, decade8) * pow(10, -12)
    # print(len(decadeList))
    return decadeList
csData = pd.DataFrame(data=[], index=[], columns=[]) 
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
pico = serial.Serial('COM9', baudrate=115200)
smu.errorqueue.clear()
smu.eventlog.clear()
smu.smua.reset()
vlist = logScale() 
# print(pow(10, -12))
# print(vlist)
# v2 = smu.ten_Vsweep(smu.smua)
# v, i = smu.Time10_Vsweep(smu.smua, 100, 0.0002, .0002)
# v1, i1, v2 = smu.idvgsChar(smu.smua, smu.smub, vlist, 0.01, .001)
commandTX = write_cmd(str(4))                                                   # selects the switch case on the pico
commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
time.sleep(.5)
print('pico confirmed: ' + str(commandRX))
v1, i1, timestamp, v2 = smu.asnyc_measAB(smu.smua, smu.smub, pow(10, -9), 60, .001, .0001)
# v1, i1, v2, i2 = smu.holdA_measAB(smu.smua, smu.smub, 10, .01, .001)
# for i in range(len(v2)):
#     v2[i] = 1.2 - v2[i]
# time.sleep(1)
print(v2)
# print(v1)
# print(timestamp)
# smu.errorqueue.count()

# csData['Time'] = timestamp
csData['V1'] = v1
csData['currIn'] = i1
# csData['v2'] = v2
print(csData)
csData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/idvsCharacterization/testcharData' + dt_string + '.csv')
plt.plot(v2, label = "Vs")
plt.yscale('log')
plt.title("RTS: Vg = 1.2 V, Vdd = 1.2 V, Ibias = 1 nA, AmpBias = .5 mA, column = 2, row = 1")
plt.xlabel("Time [mSec]")
plt.ylabel("Voltage [V]")
plt.legend()
plt.savefig(picLoc + "col2_row1.png")
fig1 = plt.show(block = False)
plt.pause(3)
plt.close(fig1)
# smu._write(value='smua.source.output = smua.OUTPUT_OFF')
# smu._write(value='smub.source.output = smub.OUTPUT_OFF')
# smu.eventlog.clear()