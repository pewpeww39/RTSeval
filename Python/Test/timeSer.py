from driverTest import Keithley2600
#from keithley2600 import Keithley2600
import numpy as np
import math
import time

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
    print(len(decadeList))
    return decadeList

smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
# smu.smua.trigger.measure.action = smu.smua.ENABLE
# smu.setA_dMeasIV(smu.smua, smu.smub, 0.0000001, 10, .1, 1)
# vlist = range(1,10,1)
# vlist = np.logspace(np.log10(pow(10,-12)), np.log10(pow(10,-5)), 200)
vlist = logScale() 
print(pow(10, -12))
print(vlist)
# smu.ten_Vsweep(smu.smua)
# v, i = smu.Time10_Vsweep(smu.smua, 100, 0.0002, .0002)
v1, i1, v2 = smu.idvgsChar(smu.smua, smu.smub, vlist, 0.001, .001)
# v1, i1, v2, i2 = smu.holdA_measAB(smu.smua, smu.smub, 10, .01, .001)
time.sleep(1)
print(v2)
print(v1)
print(i1)
# smu._write(value='smua.source.output = smua.OUTPUT_OFF')
# smu._write(value='smub.source.output = smub.OUTPUT_OFF')
# smu.eventlog.clear()