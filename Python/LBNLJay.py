import serial
import sys
import traceback
import time
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keithleyDriver import Keithley2600
from os import system, name
from datetime import datetime
from pathlib import Path
from Oscope import OScope
import os
import pyvisa
rm = pyvisa.ResourceManager()

# datetime object containing current date and time
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
pico = serial.Serial('COM6', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
p = Path.home()

def save_experiment(start_time, end_time, transients, amp, voltage, directory):
    path = Path("~/Documents/LBNL2023/" + directory + ".csv").expanduser()
    experiment = 0
    if path.exists():
        # get last experiment #
        experiment = pd.read_csv("~/Documents/LBNL2023/" + directory + ".csv", usecols = ['experiment'])['experiment'].iloc[-1] + 1
        print(experiment)
    else:
        pd.DataFrame([], columns=["experiment", "start_time", "end_time", "transients", "amp", "voltage"]).to_csv(path, index=False)

    data = {
        "experiment": experiment,
        "start_time": start_time,
        "end_time": end_time,
        "transients": transients,
        "amp": amp,
        "voltage": voltage
    }
    df = pd.DataFrame(data, index=[experiment])
    try:
        df.to_csv(path, mode='a', header=False, index=False)
    except Exception as e:
        print(e)
    # also save individual experiments to avoid any data loss
    df.to_csv(f"~/Documents/LBNL2023/" + directory + "_{experiment}_{time.time()}.csv", index=False)

def clearSMU():
    smu.errorqueue.clear()
    smu.eventlog.clear()
    smu.smua.reset()
    smu.smub.reset()

def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def save_data(iInLv, iInHv):
    data = pd.DataFrame(data={"iInHV": iInHv, "iInLV": iInLv})
    data.to_csv("~/Documents/LBNL2023/latchup/latchuptest_" + str(time.time()) + ".csv", index=False)

def doe1_Latchup(expectedLV, expectedHV, latchup_recovery_time):
    smu.smua.OUTPUT_DCVOLTS                                                 # SMU 1 is set to apply voltage
    smu.smub.OUTPUT_DCVOLTS                                                 # SUM 2 is set to measure current
    write_cmd(f"{7}")
    commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))                            # confirms pico is on
    time.sleep(0.5)
    print("Power turned on.")
    smu._write(value='smua.source.output = smua.OUTPUT_ON')
    smu._write(value='smub.source.output = smub.OUTPUT_ON')
    smu.apply_voltage(smu.smua, 1.2)
    smu.apply_voltage(smu.smub, 3.3)
    statement = True
    repreated_above_threshold = 30
    current_list = []
    current_list_1 = []
    LV_latchup_count = 0
    HV_latchup_count = 0
    print("starting")
    try:
        while statement is True:
            print("measuring...............")
            iMeasureLV = smu.smua.measure.i()
            iMeasureHV = smu.smub.measure.i()
            current_list.append(iMeasureLV)
            current_list_1.append(iMeasureHV)
            
            all_measure_LV = all([(value > expectedLV) for value in current_list[-repreated_above_threshold:]])
            all_measure_HV = all([(value > expectedHV) for value in current_list_1[-repreated_above_threshold:]])

            if (len(current_list) > repreated_above_threshold) and all_measure_LV:
                print("*************************LATCH UP LV!*************************")
                smu._write(value='smua.source.output = smua.OUTPUT_OFF')
                smu._write(value='smub.source.output = smub.OUTPUT_OFF')
                save_data(current_list, current_list_1)
                time.sleep(latchup_recovery_time)
                current_list = []
                current_list_1 =[]
                smu._write(value='smua.source.output = smua.OUTPUT_ON')
                smu._write(value='smub.source.output = smub.OUTPUT_ON')
                LV_latchup_count += 1

            if (len(current_list_1) > repreated_above_threshold) and all_measure_HV:
                print("*************************LATCH UP HV!*************************")
                smu._write(value='smua.source.output = smua.OUTPUT_OFF')
                smu._write(value='smub.source.output = smub.OUTPUT_OFF')
                save_data(current_list, current_list_1)
                time.sleep(latchup_recovery_time)
                current_list = []
                current_list_1 =[]
                smu._write(value='smua.source.output = smua.OUTPUT_ON')
                smu._write(value='smub.source.output = smub.OUTPUT_ON')
                HV_latchup_count += 1
            
            
    except:
        # print(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        save_data(current_list,current_list_1)
        smu._write(value='smua.source.output = smua.OUTPUT_OFF')
        smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    
    print(f"LV Latchups: {LV_latchup_count}")
    print(f"HV Latchups: {HV_latchup_count}")
    print('LV average: ', np.array(current_list).mean())
    print('HV average: ', np.array(current_list_1).mean())

doe1_Latchup(expectedLV=4E-05,
                 expectedHV=0.011,
                 latchup_recovery_time=2)