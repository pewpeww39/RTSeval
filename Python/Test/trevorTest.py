from os import system, name
import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithley2600 import Keithley2600
from BKPrecision import lib1785b as bk
from datetime import datetime
import numpy as np
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
pico = serial.Serial('COM4', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua
smu._write(value='smub.source.autorangev = smub.AUTORANGE_ON')  #set auto range for smua
smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
bkdmm = serial.Serial('com7', 9600)                             #set com port for BK power supply
main_df = pd.DataFrame(columns=['time', 'voltage', 'current', 'row', 'col'])
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
def run(start_voltage, stop_voltage, measurements, n_rows, n_cols, save=False):
    dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    space = np.logspace(np.log10(start_voltage), np.log10(stop_voltage), measurements)
    for row in range(n_rows):
        for col in range(n_cols):
            commandTX = write_cmd(str(3))                                                   # selects the switch case on the pico
            commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
            time.sleep(.05)
            print('pico confirmed: ' + str(commandRX))
            column = write_cmd(str(col))                                                    # increments the column to test
            columnRX = pico.read_until().strip().decode()                                   # confirms column selected
            print('pico selected column: ' + str(columnRX))
            commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
            v_smu1, i_smu1, v_smu2, i_smu2 = smu.voltage_sweep_dual_smu(smu1=smu.smua, smu2=smu.smub, smu1_sweeplist=space,  smu2_sweeplist=[0]*len(space), t_int=0.001, delay=-1, pulsed=False)
            df = pd.DataFrame({'vin': v_smu1, 'cin': i_smu1, 'vout': v_smu2, 'cout': i_smu2, 'row': [row]*len(v_smu1), 'col': [col]*len(v_smu1), 'vgg': 1.2-np.array(v_smu1)})
            main_df = main_df.concat(df, ignore_index=True)
    if save:
        main_df.to_csv('data/' + dt_string + '.csv')
    return main_df
df = run(1, 600000, 200, 1, 10, save=True)
print(df.head(10))