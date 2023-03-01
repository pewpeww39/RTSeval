from os import system, name
import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from driverTest import Keithley2600
# from keithley2600 import Keithley2600
# from BKPrecision import lib1785b as bk
from datetime import datetime
import numpy as np
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
pico = serial.Serial('COM5', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR', raise_keithley_errors=True)               #set ip addr for smu
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua
smu._write(value='smub.source.autorangev = smub.AUTORANGE_ON')  #set auto range for smua
# smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
# bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
# bkdmm = serial.Serial('com6', 9600)                             #set com port for BK power supply
main_df = pd.DataFrame(columns=['time', 'voltage', 'current', 'row', 'col'])
col = 2
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def run(start_voltage, stop_voltage, measurements, n_rows, n_cols, save=False):
    dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    space = np.logspace(np.log10(start_voltage), np.log10(stop_voltage), measurements)
    main_df = pd.DataFrame()
    for row in range(1, n_rows+1):
        for col in range(1, n_cols+1):
            start_total_time = time.time()
            commandTX = write_cmd(f"4,{row},{col}")                                                   # selects the switch case on the pico
            commandRX = tuple(pico.read_until().strip().decode().split(','))
            print(commandRX)
            commandRX, rowRX, columnRX = commandRX
            end_command_time = time.time()
            #print(tuple(pico.read_until().strip().decode().split(',')))
            # commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
            # # time.sleep(.05)
            print('pico confirmed: ' + str(commandRX))
            # write_cmd(str(1))                                              # increments the column to test
            # rowRX = pico.read_until().strip().decode()                                   # confirms column selected
            print('pico selected row: ' + str(rowRX))
            # # time.sleep(.05)
            # write_cmd(str(5))                                              # increments the column to test
            # columnRX = pico.read_until().strip().decode()                                   # confirms column selected
            print('pico selected column: ' + str(columnRX))
            # # time.sleep(.05)
            start_response_time = time.time()
            commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
            print(f'pico loaded shift register - response {commandRX}')                           # confirms shift registers are loaded
            end_response_time = time.time()
            
            start_voltage_sweep = time.time()
            v_smu1, i_smu1 = smu.voltage_sweep_single_smu(smu=smu.smua, smu_sweeplist=space, t_int=0.001, delay=0.005, pulsed=False)
            df = pd.DataFrame({'vin': v_smu1, 'cin': i_smu1, 'row': [row]*len(v_smu1), 'col': [col]*len(v_smu1), 'vgg': 1.2-np.array(v_smu1)})
            end_total_time = time.time()

            print(f"({row}, {col}) - command_time: {end_command_time-start_total_time}")
            print(f"({row}, {col}) - response_time: {end_response_time-start_response_time}")
            print(f"({row}, {col}) - sweep_time: {end_total_time-start_voltage_sweep}")
            print(f"({row}, {col}) - total_time: {end_total_time-start_total_time}")

            #v_smu1, i_smu1, v_smu2, i_smu2 = smu.voltage_sweep_dual_smu(smu1=smu.smua, smu2=smu.smub, smu1_sweeplist=space,  smu2_sweeplist=[0]*len(space), t_int=0.001, delay=-1, pulsed=False)
            #df = pd.DataFrame({'vin': v_smu1, 'cin': i_smu1, 'vout': v_smu2, 'cout': i_smu2, 'row': [row]*len(v_smu1), 'col': [col]*len(v_smu1), 'vgg': 1.2-np.array(v_smu1)})
            main_df = pd.concat([df, main_df], ignore_index=True)
    #if save:
    #    main_df.to_csv('data/' + dt_string + '.csv')
    return main_df
df = run(1e-10, 5e-5, 55, 2, 10, save=True)
print(df.head(10))