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

def clearSMU():
    smu.errorqueue.clear()
    smu.eventlog.clear()
    smu.smua.reset()
    smu.smub.reset()

aData = pd.DataFrame(data=[], index=[], columns=[]) 
bData = pd.DataFrame(data=[], index=[], columns=[])
rtsData = pd.DataFrame(data=[], index=[], columns=[])  
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
pico = serial.Serial('COM9', baudrate=115200)

commandTX = write_cmd(str(4))                                                   # selects the switch case on the pico
commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
time.sleep(.5)
print('pico confirmed: ' + str(commandRX))
v1, i1, v2 = smu.sourceA_measAB(smu.smua, smu.smub, pow(10, -9), 60, .001, .0001)
aData['V1'] = v1
aData['currIn'] = i1
bData['v2'] = v2
rtsData = pd.concat(aData, bData)
rtsData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/idvsCharacterization/testcharData' + dt_string + '.csv')
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