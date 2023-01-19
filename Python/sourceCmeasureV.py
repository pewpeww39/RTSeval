import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithley2600 import Keithley2600

smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')   #set ip addr for smu
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua 
smu.set_integration_time(smu.smua, 0.001)  # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")   #set v liimit smub

dmmData = pd.DataFrame(data=[], index=[], columns=[])   #create dataframe

while True:
    currIn = smu.apply_current(smu.smua, 0.000000000005)
    smuA_VOut = smu.smua.measure.v()
