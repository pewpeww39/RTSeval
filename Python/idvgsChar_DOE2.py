from os import system, name
import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithleyDriver import Keithley2600
#from keithley2600 import Keithley2600
# from BKPrecision import lib1785b as bk
from datetime import datetime
import numpy as np
import pyvisa
rm = pyvisa.ResourceManager()
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

pico = serial.Serial('COM3', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu2 = Keithley2600('TCPIP0::192.168.4.12::INSTR') 
powerSupply = rm.open_resource('TCPIP0::192.168.4.3::INSTR')
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua 
smu._write(value='smub.source.autorangev = smub.AUTORANGE_OFF')  #set auto range for smua 
# smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
# bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
# bkdmm = serial.Serial('com7', 9600)                             #set com port for BK power supply
# def logScale(start, stop, power):
def logScale():
    decadeList = np.logspace(np.log10(1e-10), np.log10(5e-5), 50)
    return decadeList
    
def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def powerPico():                                                                    # Turns on the vPwr pins for pi pico
    write_cmd(str(7))                                                               # selects the switch case on the pico
    pico.read_until().strip().decode()                                              # confirms mode selected
    print('pico turned on the power') 
    time.sleep(2)

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
        sweepList = (-1e-8, -1e-4, 10, 0)
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
        colStart = 96 + 1
        colEnd = colStart + 16
        sweepList = (-1e-8, -4e-4, 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 6\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 7/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 7:
        colStart = 112 + 1
        colEnd = colStart + 16
        sweepList = (-1e-8, -1e-5, 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\jacob\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 7\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 7/idvgscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    return rowStart, rowEnd, colStart, colEnd, sweepList, csIn, picLoc, fileLoc, measDelay, nplc, limiti, rangei, vg

def idvgsCharacterization(bank, dieX, dieY, bypass):
    currIn = []
    measVs = []
    measVI = []
    vGS = []
    spec = []
    idvgsData = pd.DataFrame(data=[], index=[], columns=[])  
    # pltData = pd.DataFrame(data=[], index=[], 
    #                     columns=['Site', 'Type', 'V_C Out', 'Vsg', 'Iref', "V_iref", 'W/L', 'Temp(K)', 'Die X', 'Die Y',
    #                                 'Vth', 'Gm', 'Swing Factor', 'Row', 'Column', 'Test Time (Sec)'])                         #create dataframe
    pltData = pd.DataFrame(data=[], index=[], 
                        columns=['Site', 'V_C Out', 'Vsg', 'Iref', 'Id', "V_iref",  'Temp(K)', 'Die X', 'Die Y',
                                    'Row', 'Column', 'Test Time (Sec)'])  
    specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\skywater\RTSeval\Files\RTS_Array_Cells.csv',
                        index_col=[0] , header=0), columns = ['W/L', 'Type'])
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

# idvgsCharacterization(0, '5L', '3', True) #Old Chip
idvgsCharacterization(0, '2E', '6', True) #New Chip currently being measured
# idvgsCharacterization(0, '4M', '3', True) #Test Chip