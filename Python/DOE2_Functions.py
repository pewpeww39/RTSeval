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

# datetime object containing current date and time
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
# oscope = OScope("TCPIP0::192.168.4.2::inst0::11
# INSTR")
pico = serial.Serial('COM3', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu2 = Keithley2600('TCPIP0::192.168.4.12::INSTR')
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

def bankNum(bank, bypass):
    rowStart = 0 + 1
    rowEnd = rowStart + 1 
    # rowStart = 0 + 1
    # rowEnd = 1 + 1 
    if bypass is True and bank in [0,1,2,3]:
        select = 3
    elif bypass is False and bank in [0,1,2,3]:
        select = 3
    elif bypass is True and bank in [4,5,6,7]:
        select = 6
    elif bypass is False and bank in [4,5,6,7]:
        select = 4
    else:
        print('Bypass not selected')
        select = 0
    if bank == 0:
        # colStart = 0 + 1
        # colEnd = 8 + 1 #colStart + 32
        colStart = 0 + 1
        # colEnd = colStart + 16
        colEnd = colStart + 16 #17
        sweepList = (-1e-8, -1e-4, 50, 0)
        csIn = select
        # picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 1\\idvscharData"
        # fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization\\Bank 1\\idvscharData'
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 0\\idvgscharData"
        fileLoc = '~\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 0\\idvgscharData'
        measDelay = -1
        nplc = 16/60
        limiti = 0.001
        rangei = pow(10, -3)
        vg = 3.3
    elif bank == 1:
        # colStart = 33
        # colEnd = colStart + 32
        colStart = 16 + 1
        colEnd = colStart + 16
        sweepList = (-1e-8, -4e-4, 50, 0)
        csIn = select
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 1\\idvscharData"
        fileLoc = '~\\Documents\\SkywaterData\\idvgsCharacterization\\Bank 2\\idvscharData'
        measDelay = -1
        nplc = 16/60
        limiti = 0.001
        rangei = pow(10, -3)
        vg = 1.2
    elif bank == 2:
        colStart = 32 + 1
        colEnd = colStart + 16
        sweepList = (-1e-8, -4e-4, 50, 0)
        csIn = select
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 2\\idvscharData"
        fileLoc = '~\\Documents\\SkywaterData\\idvgsCharacterization\\Bank 3\\idvscharData'
        measDelay = -1
        nplc = 16/60
        limiti = 0.01
        rangei = pow(10, -2)
        vg = 1.2
    elif bank == 3:
        colStart = 48 + 1
        colEnd = colStart + 16
        sweepList = (-1e-8, -4e-4, 50, 0)
        csIn = select
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 3\\idvscharData"
        fileLoc = '~\\Documents\\SkywaterData\\idvgsCharacterization\\Bank 4\\idvscharData'
        measDelay = -1
        nplc = 16/60
        limiti = 0.001
        rangei = pow(10, -3)
        vg = 3.3
    elif bank == 4:
        colStart = 64 + 1
        colEnd = colStart + 16
        sweepList = (-1e-8, -4e-4, 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 4\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 5/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 5:
        colStart = 81
        colEnd = colStart + 16
        sweepList = (-1e-8, -4e-4, 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 5\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 6/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 6:
        colStart = 96
        colEnd = colStart + 16
        sweepList = (-1e-8, -4e-4, 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 6\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 7/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 7:
        colStart = 113
        colEnd = colStart + 16
        sweepList = (-1e-8, -1e-5, 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 7\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 7/idvgscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    return rowStart, rowEnd, colStart, colEnd, sweepList, csIn, picLoc, fileLoc, measDelay, nplc, limiti, rangei, vg

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
    return

def idvgsCharacterization(bank, dieX, dieY, bypass):
    currIn = []
    measVs = []
    measVI = []
    vGS = []
    spec = []
    idvgsData = pd.DataFrame(data=[], index=[], columns=[])  
    pltData = pd.DataFrame(data=[], index=[], 
                        columns=['Site', 'V_C Out', 'Vsg', 'Iref', 'Id', "V_iref",  'Temp(K)', 'Die X', 'Die Y',
                                    'Row', 'Column', 'Test Time (Sec)'])  
    # specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\skywater\RTSeval\Files\RTS_Array_Cells.csv',
    #                     index_col=[0] , header=0), columns = ['W/L', 'Type'])
    debug = False
    row = 0

    rowStart, rowEnd, colStart, colEnd, sweepList, csIn, picLoc, fileLoc, measDelay, nplc, limiti, rangei, vg = bankNum(bank, bypass)

    smu.apply_current(smu.smua, 0.0)
    smu.apply_current(smu.smub, 0.0)
    smu2.apply_current(smu2.smua, 0.0)
    powerSupply_Set("P25V", "5.333", "1.0")
    powerSupply_On()
    powerPico()
    start_total_time = time.time()
    plt.figure(figsize=(12,14))
    for row in range(rowStart, rowEnd):
        for col in range(colStart, colEnd):
            write_cmd(f"{csIn},{row},{col}")                                                   # selects the switch case on the pico
            commandRX = tuple(pico.read_until().strip().decode().split(','))
            if debug is True:
                print(commandRX)
            commandRX, rowRX, columnRX = commandRX
            rowRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                    rowRX)  
            columnRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the colimn number
                    columnRX)    
            print('pico confirmed: ' + str(commandRX))
            print('pico selected row: ' + str(rowRX))
            print('pico selected column: ' + str(columnRX))
            commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
            print(f'pico loaded shift register.')                           # confirms shift registers are loaded
            spec = list(specData.iloc[col-1])
            currIn, measVI, measVs = smu.idvgsChar(smu.smub, smu.smua, sweepList, measDelay, nplc)
            currIn = [abs(ele) for ele in currIn]
            pltData["V_C Out"] = measVs
            pltData['Site'] = 'IU'
            # pltData['Type'] = spec[1]
            vSG = np.full_like(measVs, vg) - measVs 
            pltData["V_iref"] = measVI
            pltData["Vsg"] = vSG # [1.2 - measVs for i in range(len(measVs))]
            pltData["Iref"] = currIn
            pltData["Id"] = pltData["Iref"]/10
            # pltData["W/L"] = spec[0]
            pltData["Temp(K)"] = 295
            pltData["Die X"] = dieX
            pltData["Die Y"] = dieY
            # pltData["Gm"] = np.gradient(currIn, vGS)
            # grouped = pltData.groupby(pltData.Gm)
            # maxGm = max(np.gradient(pltData['Id'], pltData['Vgs'], edge_order=2))
            # vthData = grouped.get_group(max(pltData['Gm']))
            # pltData["Vth"] = (vthData.Vgs*maxGm - np.sqrt(abs(vthData.Id)))/maxGm
            pltData["Row"] = rowRX
            pltData['Column'] = columnRX
            print(pltData)
            if debug is True:
                print(len(measVs))
                print(vGS)

            # if ((col % 2 == 1) and (row <= 97)):
               
            plt.subplot(2,1,1)
            plt.title("$I_{d}$ [A] vs $V_{C}$ Out")
            plt.plot(pltData["Id"], pltData["V_C Out"], label = "Id" + str(col))
            plt.xscale('log')
            plt.ylabel("$V_{C}$ [V]")
            plt.legend()
            plt.xlabel("$I_{d}$ [A]")

            plt.subplot(2,1,2)
            plt.title("$I_{d}$ [A] vs $V_{sg}$ Out")
            plt.plot(pltData["Id"], pltData["Vsg"], label = "Id" + str(col))
            plt.xscale('log')
            plt.ylabel("$V_{sg}$ [V]")
            plt.legend()
            plt.xlabel("$I_{d}$ [A]")


        plt.figtext(.35, .95, "$I_{Ref}$ = " + str(sweepList[0]) 
                    + " A to " + str(sweepList[1]) + " A", fontsize = 15)
        plt.figtext(.4, .92, "Current Sweep", fontsize = 15)
        plt.savefig(picLoc + "R" + rowRX + 'C' + columnRX + "currentSweep.png")
        plt.tight_layout()
        plt.show(block = False)
        plt.close()

        currIn = []
        measVs = []
        measVI = []
        vGS = []
        commandRX=0
        idvgsData = pd.concat([idvgsData, pltData], axis = 0, ignore_index=True)
        idvgsData.to_csv(fileLoc + 'BAK.csv')
    
    
    write_cmd(str(9))                                                   # selects the switch case on the pico
    commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
    print('pico confirmed: ' + str(commandRX) + ' and reset the shift registers')   

    end_total_time = time.time()
    test_time = end_total_time - start_total_time
    idvgsData.at[0, 'Test Time (Sec)'] = test_time
    idvgsData.to_csv(fileLoc + dt_string + '.csv')
    # print(idvgsData)
    smu._write(value='smua.source.output = smua.OUTPUT_OFF')
    smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    smu2._write(value='smua.source.output = smua.OUTPUT_OFF')
    powerSupply_Off()
    return

def doe1_ShiftRegister(seconds):
    # oscope.set_thresholds(3.1, 3.5, 1)          # tells oscope the clock is set to HIGH
    # oscope.set_thresholds(3.5, 4, 2)            # watches vertical SR for upsets
    # oscope.set_thresholds(3.5, 4, 3)            # watches horizontal SR for upets
    # oscope.load_setup("SR_SEU.setup?")              # loads the setup for this tets

    powerSupply_Set("P25V", "5.2", "1.0")
    powerSupply_On()
    write_cmd(f"{7}")
    commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))                            # confirms pico is on
    time.sleep(1)
    print("Power is turned on.")
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
try:
    if test == 1:
        print("Amp Characterization is selected.")
        amp = int(input("Which amp are you running? "))
        doe1_ampCharacterization(amp, 1)   # (amp, test)

    elif test == 2:
        print("Current sweep test is selected.")
        bank = int(input("Which bank are you running? "))
        idvgsCharacterization(bank, '2E', '6', True)   # (bank, DieX, DieY, Bypass)
        
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
except:
    print("Abort")