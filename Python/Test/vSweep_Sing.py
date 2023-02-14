from driverTest import Keithley2600
#from keithley2600 import Keithley2600
import numpy as np
import math
import time

# smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
# smu._write(value='smua.source.autorangev = smua.AUTORANGE_ON')  #set auto range for smua 

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
    decadeList = np.append(decadeList, decade8)
    print(len(decadeList))
    return decadeList
    # length = len(decadeList)
    # for a in range(length):
    #     # print(decadeList[a]*.0000000001)
    #     print(a)
    #     #smu.apply_current(smu.smua, decadeList[a]*.0000000001)
    #     time.sleep(.1)
    

# vlist = frange(1, 5, .5)
vlist = (1, 10, 11, 0)
# vlist = [.0001, 0.0002, 0.0003, 0.0004, .0005, 0.0006, 0.0007, 0.0008, 0.0009]
# logV = math.log10(20)
# vlist = [0, 1.2, 1001, 0]
# print(logV)

# vlist = logScale()
print(vlist)
# smu.voltage_sweep_single_smu(smu.smua, vlist, 0.001, 1, False)
# smu.vLog_sing(smu.smua, vlist, 0.001, 1, False)
# smu._write(value = "smua.trigger.source.logv(1, 10, 11, 0)")
# smu._write(value = "smua.trigger.source.action = smua.ENABLE")
# smu._write(value='smua.source.output = smua.OUTPUT_OFF')
