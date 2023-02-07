from keithley2600 import Keithley2600
from BKPrecision import lib1785b as bk
import pandas as pd
import matplotlib.pyplot as plt
from os import system, name
from datetime import datetime
import serial
import sys
import time
import re
import numpy as np
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
csData = pd.DataFrame(data=[], index=[], columns=[])
def frange(start: int, end: int, step: float):
    """
    Generate a list of floating numbers within a specified range.

    :param start: range start
    :param end: range end
    :param step: range step
    :return:
    """
    numbers = np.linspace(start, end,(end-start)*int(1/step)+1).tolist()
    return [round(num, 2) for num in numbers]


dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu.smua.sense = smu.smua.SENSE_LOCAL
smu.smub.sense = smu.smub.SENSE_LOCAL
smu._write(value='smua.source.rangev = ' + '10')
smu._write(value='smub.source.rangev = 10')
smu._write(value= 'smua.source.limitv = 10')                   #set v limit smua
smu._write(value= "smub.source.limitv = 10")                   #set v limit smub

plc = .001
intTime = plc / 60
#smuaV = frange(1, 5, 1)
smuaV = range(4,6)
smubV = frange(0, 5, .1)

#output = smu.voltage_sweep_meas_curr(smu.smub, smu.smua, smubV, 0.0001, -1, False)
csData = smu.output_measurement(smu.smua, smu.smub, 0, 10, .1, smuaV, intTime, 0.0001 , False)
#output = smu.voltage_sweep_dual_smu(smu.smua, smu.smub, smuaV, smubV, intTime, 0.1, False)
csData.save_csv('C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\obcmCharacterization\\obcmCharData' + dt_string + '.csv')
fig = csData.plot(0, [2,5])
plt.savefig("C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\obcmCharacterization\\obcmCharData" + dt_string + ".png")
plt.pause(5)
# plt.plot(csData.VoltIn, csData.CurrOut001, label = "vgs=3")