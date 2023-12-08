import serial
import sys
import time
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keithleyDriver import Keithley2600
from os import system, name
from datetime import datetime
from pathlib import Path
# from Oscope import OScope
import os
import pyvisa
rm = pyvisa.ResourceManager()

pico = serial.Serial('COM3', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
# smu2 = Keithley2600('TCPIP0::192.168.4.12::INSTR')
powerSupply = rm.open_resource('TCPIP0::192.168.4.3::INSTR') 
smu._write(value= 'node[1].smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "node[1].smub.source.limitv = 3.3")                   #set v liimit smub
smu._write(value= 'node[2].smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "node[2].smub.source.limitv = 3.3")   

node = smu.dualSMU(smu.smua, smu.smub) #, smu2.smua, smu2.smub)
time.sleep(2)
# smu.smua.OUTPUT_DCVOLTS         # SMU 1 is set to apply voltage
# smu.smub.OUTPUT_DCAMPS           # SUM 2 is set to measure voltage
# smu.smua.OUTPUT_ON         # SMU 1 is set to apply voltage
# smu.smub.OUTPUT_ON           # SUM 2 is set to measure voltage
# smu.apply_current(smu.node[1].smua, 0.0)
# smu.apply_current(smu.node[1].smub, 0.0)
# smu.apply_voltage(smu.node[2].smua, 0.0)
# smu.apply_current(smu.node[2].smub, 0.0)

vList = (0, 3.3, 50)
delay = .001
t_int = 1.6/60
# vsmu1, node = smu.doe2AmpChar(smu.smub, smu.smua, vList, delay, t_int)
# smu._write(value="node[1].execute('smua.trigger.initiate()')")
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
# smu.node[1].smua.source.output = smu.OUTPUT_OFF
smu._write(value='node[2].smua.source.output = smua.OUTPUT_OFF')
smu._write(value='node[2].smub.source.output = smub.OUTPUT_OFF')
# smu._write(value='node[1].smua.reset')
# smu._write(value='node[1].smub.reset')
# smu._write(value='node[2].smua.reset')
# smu._write(value='node[2].smub.reset')
# smu._write(value='node[1].smua.errorque.clear()')
# smu._write(value='node[1].smub.errorque.clear()')
# smu._write(value='node[2].smua.errorque.clear()')
# smu._write(value='node[2].smub.errorque.clear()')
# smu.smua.reset()
# smu.smub.reset()
print(node)