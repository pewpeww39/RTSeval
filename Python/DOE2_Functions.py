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
from Oscope import OScope
import os
import pyvisa
rm = pyvisa.ResourceManager()

# datetime object containing current date and time
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
# oscope = OScope("TCPIP0::192.168.4.2::inst0::11
# INSTR")
pico = serial.Serial('COM6', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
powerSupply = rm.open_resource('TCPIP0::192.168.4.3::INSTR') 
p = Path.home()

def powerSupply_Set(channel, voltage, current):
    powerSupply.write("INST "+channel) # Select +6V output ch 1
    powerSupply.write("VOLT "+voltage) # Set output voltage to 3.0 V
    powerSupply.write("CURR "+current) # Set output current to 1.0 A

def powerSupply_On():
    powerSupply.write("OUTP ON")

def powerSupply_Off():
    powerSupply.write("INST P6V")
    powerSupply.write("OUTP OFF")
    powerSupply.write("INST P25V")
    powerSupply.write("OUTP OFF")
    powerSupply.write("INST N25V")
    powerSupply.write("OUTP OFF")



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
    except Exception as e:3
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

def doe1_ampCharacterization(amp, test):
    clearSMU()
    if amp in range(0,4):
        select = 1                                                            # NMOS Op-Amp
    elif amp in range(4,8):
        select = 2                                                            # PMOS Op-Amp

    data = pd.DataFrame(data=[], index=[], columns=["vIn", "vOut"])           #create dataframe

    
    powerSupply_Set("P25V", "5.2", "1.0")
    powerSupply_On()
    write_cmd(f"{7}")
    commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))                            # confirms pico is on
    time.sleep(1)
    print("Power is turned on.")
    # powerSupply_Set("P6V", "3.3", "1.0")
    # powerSupply_On()
    # powerSupply_Set("N25V", "1.2", "1.0")
    # powerSupply_On()

    smu.smua.OUTPUT_DCVOLTS          # SMU 1 is set to apply voltage
    smu.smub.OUTPUT_DCAMPS           # SUM 2 is set to measure voltage
    # smu._write(value='smua.source.output = smua.OUTPUT_OFF')
    # smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    time.sleep(1)
    write_cmd(f"{select}")  
    time.sleep(0.5)
    commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))                            # confirms amp characterization is selected
    # if commandRX == 1 or commandRX == 2:
    print('pico selected amp characterization procedure.')
    vList = (0, 3.3, 50)
    # vList = (0, .3, 30)
    delay = 0
    t_int = 0.005
    smu._write(value = "smub.measure.autozero = smub.AUTOZERO_AUTO")
    smu._write(value='smua.source.output = smua.OUTPUT_ON')
    smu._write(value='smub.source.output = smub.OUTPUT_ON')
    time.sleep(1)
    # smu.apply_voltage(smu.smua, 1.8)
    smu.smub.measure.v()
    # print(test)
    time.sleep(5)
    # start_time, end_time, transients = oscope.save_measurements_timed(3)
    data.vIn, data.vOut = smu.doe1AmpChar(smu.smub, smu.smua, vList, delay, t_int)
    print(data)
    plt.plot(data.vIn, data.vOut, label = '0.5 mA')
    plt.title("Vin vs Vout")
    plt.xlabel("Vin")
    plt.ylabel("Vout")
    plt.legend()
    plt.savefig(str(p) + "\\Documents\\SkywaterData\\DOE2\\ampCharacterization\\amp" + str(amp) + "_Vo_vs_Vin_testNumber_" + str(test) + ".png")
    fig = plt.show(block=False)
    plt.pause(3)
    plt.close(fig)
    commandTX = write_cmd(f"{9}")          
    # print(data)
    data.to_csv("~/Documents/SkywaterData/DOE2/ampCharacterization/amp" + str(amp) + '.csv')
    smu._write(value='smua.source.output = smua.OUTPUT_OFF')
    smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    powerSupply_Off()

def save_data(iInHv, iInLV):
    data = pd.DataFrame(data={"iInHV": iInHv, "iInLV": iInLV})
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
            
            all_measure_LV = all(value > expectedLV for value in current_list[:-repreated_above_threshold])
            all_measure_HV = all(value > expectedHV for value in current_list_1[:-repreated_above_threshold])
            
            if ((len(current_list) > repreated_above_threshold) or (len(current_list_1) > repreated_above_threshold)) and (all_measure_LV or all_measure_HV):
                print("*************************LATCH UP!*************************")
                smu._write(value='smua.source.output = smua.OUTPUT_OFF')
                smu._write(value='smub.source.output = smub.OUTPUT_OFF')
                save_data(current_list, current_list_1)
                time.sleep(latchup_recovery_time)
                current_list = []
                current_list_1 =[]
                smu._write(value='smua.source.output = smua.OUTPUT_ON')
                smu._write(value='smub.source.output = smub.OUTPUT_ON')
                LV_latchup_count += 1
                HV_latchup_count += 1
            
            
    except:
        save_data(current_list, current_list_1)
        smu._write(value='smua.source.output = smua.OUTPUT_OFF')
        smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    
    print(f"LV Latchups: {LV_latchup_count}")
    print(f"HV Latchups: {HV_latchup_count}")
    print('LV: ', current_list)
    print('HV: ', current_list_1)

def doe1_Tranisents(amp, voltage, seconds):
    # data = pd.DataFrame(data=[], index=[], columns=["vIn", "iIn"])          # create dataframe

    smu.smua.OUTPUT_DCVOLTS                                                 # SMU 1 is set to apply voltage
    smu.smub.OUTPUT_DCVOLTS                                                 # SUM 2 is set to measure current
    smu._write(value='smua.source.output = smua.OUTPUT_ON')
    # smu._write(value='smub.source.output = smub.OUTPUT_ON')
    if amp in range(0,4):
        select = 1                                                            # NMOS Op-Amp
    elif amp in range(4,8):
        select = 2   
    write_cmd(f"{7}")
    commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))                            # confirms pico is on
    time.sleep(0.5)
    print("Power turned on.")
    write_cmd(f"{select}")  
    time.sleep(0.5)
    commandRX = tuple(pico.read_until().strip().decode())  
    print('pico selected SET Transient procedure.')
    smu.apply_voltage(smu.smua, voltage)
    
    start_time, end_time, transients = oscope.save_measurements_timed(seconds)
    # record data
    save_experiment(start_time, end_time, transients, amp, voltage, "transient/experiment")

    commandTX = write_cmd(f"{9}")          
    smu._write(value='smua.source.output = smua.OUTPUT_OFF')
    smu._write(value='smub.source.output = smub.OUTPUT_OFF')

def doe1_ShiftRegister_SEU(seconds):
    # oscope.set_thresholds(3.1, 3.5, 1)          # tells oscope the clock is set to HIGH
    # oscope.set_thresholds(3.5, 4, 2)            # watches vertical SR for upsets
    # oscope.set_thresholds(3.5, 4, 3)            # watches horizontal SR for upets
    # oscope.load_setup("SR_SEU.setup?")              # loads the setup for this tets

    print("Power is turned on.")
    powerSupply_Set("P6V", "3.3", "1.0")
    powerSupply_On()
    powerSupply_Set("N25V", "1.2", "1.0")
    powerSupply_On()
    write_cmd(f"{8}")  
    time.sleep(0.5)
    commandRX = tuple(pico.read_until().strip().decode())  
    print('pico selected SEU Shift Register procedure.')
    # h_upsets, v_upsets = oscope.report_transients(seconds)    # Script that tells oscope to count triggers over test period
    time.sleep(5)
    # time.sleep(seconds)
    write_cmd(f"{8}")
    time.sleep(0.5)
    commandRX = tuple(pico.read_until().strip().decode()) 
    powerSupply_Off()
# Test selection script

test = int(input("Which test are you running? "))

if test == 1:
    print("Amp Characterization is selected.")
    amp = int(input("Which amp are you running? "))
    doe1_ampCharacterization(amp, 1)   # (amp, test)
elif test == 2:
    print("Latch up test is selected.")
    doe1_Latchup(expectedLV=.00016, # LV threshold
                 expectedHV=.0005, #input("Enter Latch_up Threshold: "), # HV threshold
                 latchup_recovery_time=2
    )
elif test == 3:
    print("Op amp Transient test is selected.")
    doe1_Tranisents(amp=0, voltage= float(input("What Vin? ")), seconds=int(input("How long in sec? "))) # desired voltage

elif test == 4:
    print("Selected Shift Register SEU Test")
    fileLoc = str(p) + "/Documents/LBNL2023/ShiftRegisterSEU/runlog.csv"
    path = Path(fileLoc)
    if path.exists():
        seuData = pd.read_csv(fileLoc) 
        testNumber = seuData.loc[len(seuData.Test)-1, "Test"] + 1 
    else:
        seuData = pd.DataFrame(data=[], index=[], columns=["Beam Energy", "Ion", "LET", "Fluence", "Ion Energy", 
                                                            "Flux", "Time", "HorizontalSR_Upsets", 
                                                            "VerticalSR_Upsets", "Test", "H_DataState",
                                                            "V_DataState", "H_XS", "V_XS"])
        testNumber = 0
    MeV = int(input("Beam MeV: "))
    ion = str(input("Beam Ion: "))
    test_time = int(input("Total Test time input: "))
    flux = int(input("Flux Input: "))
    h_dataS = str(input("Horizontal steady state condition: "))
    v_dataS = str(input("Vertical steady state condition: "))
    start_time = time.time()
    time.sleep(1)
    braggCurve = (pd.read_csv("~/Documents/LBNL2023/Bragg Curves/In-Vacuum_" + str(MeV) + "MeV_" + ion + ".csv",
                                    header=None, names=['Depth(um)', 'depth', 'LET', 'MEV'],
                                     index_col=False, skipfooter=1, engine='python'))
    print(braggCurve)
    let = braggCurve.LET.loc[braggCurve.depth ==  23.5]
    energy = braggCurve.MEV.loc[braggCurve.depth ==  23.5]
    print("LET: " + str(energy.values))
    
    # h_upsets, v_upsets = doe1_ShiftRegister_SEU(test_time)
    h_upsets, v_upsets = [4,5]

    fluence = flux * test_time
    seuData.at[testNumber, "Test"] = testNumber
    seuData.at[testNumber, "Beam Energy"] = MeV
    seuData.at[testNumber, "Ion"] = ion
    seuData.at[testNumber, "LET"] = let.values
    seuData.at[testNumber, "Ion Energy"] = energy.values
    seuData.at[testNumber, "HorizontalSR_Upsets"] = h_upsets
    seuData.at[testNumber, "VerticalSR_Upsets"] = v_upsets
    seuData.at[testNumber, "H_DataState"] = h_dataS
    seuData.at[testNumber, "V_DataState"] = v_dataS
    seuData.at[testNumber, "Time"] = test_time
    seuData.at[testNumber, "Flux"] = flux
    seuData.at[testNumber, "Fluence"] = fluence
    seuData.at[testNumber, "H_XS"] = h_upsets / fluence
    seuData.at[testNumber, "V_XS"] = v_upsets / fluence

    seuData.to_csv(fileLoc, index=False)

