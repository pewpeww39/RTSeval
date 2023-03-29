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

dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

pico = serial.Serial('COM4', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua 
smu._write(value='smub.source.autorangev = smub.AUTORANGE_OFF')  #set auto range for smua 
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub

def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def bankNum(bank):
    rowStart = 1
    rowEnd = 96 + 1 
    if bank == 1:
        colStart = 1
        colEnd = colStart + 32
        colS = "Col000"   
        rowS = "Row00"
        sweepList = np.linspace(0, 1.2)
        vdList = [0.1, 0.8] 
        csIn = 5
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgCharacterization\\Bank 1\\idvgcharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgCharacterization/Bank 1/idvgcharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 2:
        colStart = 33
        colEnd = colStart + 32
        colS = "Col032"   
        rowS = "Row00"
        sweepList = np.linspace(0, 1.2)
        vdList = [0.1, 0.8]
        csIn = 5
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgCharacterization\\Bank 2\\idvgcharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgCharacterization/Bank 2/idvgcharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 3:
        colStart = 65
        colEnd = colStart + 32
        colS = "Col064"   
        rowS = "Row00"
        sweepList = np.append(np.linspace(0, 3.3), np.linspace(0, 3.3)) 
        vdListA = np.full(50, 0.1)
        vdListB = np.full(50, 1.5)
        vdList = np.append(vdListA, vdListB)
        csIn = 5
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgCharacterization\\Bank 3\idvgcharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgCharacterization/Bank 3/idvgcharData'
        limiti = 0.01
        rangei = pow(10, -2)
    elif bank == 4:
        colStart = 97
        colEnd = colStart + 32
        colS = "Col096"   
        rowS = "Row00"
        sweepList = np.linspace(0, 3.3)
        vdList = [0.1, 1.5] 
        csIn = 5
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgCharacterization\\Bank 4\\idvgcharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgCharacterization/Bank 4/idvgcharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 5:
        colStart = 129
        colEnd = colStart + 32
        colS = "Col128"   
        rowS = "Row00"
        sweepList = np.linspace(1.2, 0)
        vdList = [1.1, 0.4] 
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgCharacterization\\Bank 5\\idvgcharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgCharacterization/Bank 5/idvgcharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 6:
        colStart = 161
        colEnd = colStart + 32
        colS = "Col160"   
        rowS = "Row00"
        sweepList = np.linspace(0, 3.3)
        vdList = [3.2, 1.8] 
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgCharacterization\\Bank 6\\idvgcharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgCharacterization/Bank 6/idvgcharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 7:
        colStart = 193
        colEnd = colStart + 32
        colS = "Col192"   
        rowS = "Row00"
        sweepList = np.linspace(3.3, 0)
        vdList = [3.2, 1.8] 
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgCharacterization\\Bank 7\\idvgcharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgCharacterization/Bank 7/idvgcharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 8:
        colStart = 225
        colEnd = colStart + 32
        colS = "Col224"   
        rowS = "Row00"
        sweepList = np.linspace(3.3, 0)
        vdList = [3.2, 1.8] 
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgCharacterization\\Bank 8\\idvgcharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgCharacterization/Bank 8/idvgcharData'
        limiti = 0.001
        rangei = pow(10, -3)
    return rowStart, rowEnd, colStart, colEnd, colS, rowS, sweepList, vdList, csIn, picLoc, fileLoc, limiti, rangei

def powerPico():                                                                    # Turns on the vPwr pins for pi pico
    write_cmd(str(7))                                                               # selects the switch case on the pico
    pico.read_until().strip().decode()                                              # confirms mode selected
    print('pico turned on the power') 
    time.sleep(2)

currOut = []
measVd = []
measVg = []
spec = []
vdvgData = pd.DataFrame(data=[], index=[], columns=[])  
pltData = pd.DataFrame(data=[], index=[], 
                       columns=['Site', 'Type', 'Vd', 'Vg', 'Id', 'W/L', 'Temp(K)', 'Die X', 'Die Y',
                                 'Vth', 'Gm', 'Swing Factor', 'Row', 'Column'])                         #create dataframe
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W/L', 'Type'])

dieX = '6p'
dieY = '3'

rowStart, rowEnd, colStart, colEnd, colS, rowS, sweepList, vdList, csIn, picLoc, fileLoc, limiti, rangei = bankNum(6)        # selects the bank to test
colBegin = colS
smu.apply_voltage(smu.smua, 0.0)
smu.apply_voltage(smu.smub, 0.0)
powerPico()

for row in range(rowStart, rowEnd):
    for col in range(colStart, colEnd):
        # start_total_time = time.time()
        commandTX = write_cmd(f"{csIn},{row},{col}")                                                   # selects the switch case on the pico
        commandRX = tuple(pico.read_until().strip().decode().split(','))
        commandRX, rowRX, columnRX = commandRX
        # end_command_time = time.time()
        rowRX = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                rowRX)  
        columnRX = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the colimn number
                columnRX)    
        print('pico confirmed: ' + str(commandRX))
        print('pico selected row: ' + str(rowRX))
        print('pico selected column: ' + str(columnRX))
        # start_response_time = time.time()
        commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
        print(f'pico loaded the shift registers')                           # confirms shift registers are loaded
        # end_response_time = time.time()
        # start_voltage_sweep = time.time()
        spec = list(specData.iloc[col-1])
        smu._write(value = "smua.measure.autozero = smua.AUTOZERO_AUTO")
        smu.smub.measure.v()
        currOut, measVd, measVg= smu.idvgChar(smu.smua, smu.smub, sweepList, vdList, .001, .01, limiti, rangei)
        # vGS = measVs 
        # for i in range(len(measVs)):
        #     vGS[i] = 1.2 - vGS[i]
        # print(vGS)
        # pltData["Vgs"] = vGS # [1.2 - measVs for i in range(len(measVs))]
        pltData["Vd"] = measVd
        pltData["Vg"] = measVg
        pltData["Id"] = currOut
        # print(pltData['Id'])
        pltData1Id = pltData.loc[:49, 'Id']
        pltData2Id = np.sqrt(abs(pltData.loc[50:99, 'Id']))
        pltData1Vg = pltData.loc[:49, 'Vg']
        pltData2Vg = pltData.loc[50:99, 'Vg']
        pltGm1 = np.gradient(pltData1Id, pltData1Vg)
        pltGm2 = np.gradient(pltData2Id, pltData2Vg)
        maxGm1 = max(np.gradient(pltData1Id, pltData1Vg, edge_order=2))
        maxGm2 = max(np.gradient(pltData2Id, pltData2Vg, edge_order=2))
        pltData['Site'] = 'UTC'
        pltData['Type'] = spec[1]
        pltData["W/L"] = spec[0]
        pltData["Temp(K)"] = 295
        pltData["Die X"] = dieX
        pltData["Die Y"] = dieY
        pltData["Gm"] = np.append(pltGm1, pltGm2)
        grouped = pltData.groupby(pltData.Gm) 
        vthData1 = grouped.get_group(max(pltGm1))
        vthData2 = grouped.get_group(max(pltGm2))
        vthCal1 = (vthData1.Vg*maxGm1 - vthData1.Id)/vthData1.Gm -0.05
        vthCal2 = (vthData2.Vg*maxGm2 - np.sqrt(abs(vthData2.Id)))/maxGm2
        pltVth1 = np.full_like(pltData1Id, vthCal1)
        pltVth2 = np.full_like(pltData2Id, vthCal2)
        pltData["Vth"] = np.append(pltVth1, pltVth2)
        # swingF1 = (pltVth1 - np.full_like(pltVth1,vthCal1))/np.gradient(pltData1Id)
        # swingF2 = np.full_like(pltData2Id, vthCal2-0)/np.gradient(pltData2Id)
        # pltData['Swing Factor'] = np.append(swingF1, swingF2)
        pltData["Row"] = row
        pltData['Column'] = col

        if ((col % 2 == 1) and (row <= 2)):
            vth1 = pltData.at[1, "Vth"]
            vth2 = pltData.at[51, "Vth"]
            grouped = pltData.groupby(pltData.Vth) 
            pltData1 = grouped.get_group(vth1)
            pltData2 = grouped.get_group(vth2)
            plt.plot(pltData1["Vg"], pltData1["Id"], label = "Vd = " + str(vdList[0]))
            plt.plot(pltData2["Vg"], pltData2["Id"], label = "Vd = " + str(vdList[1]))
            # plt.figtext(.4, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            # plt.figtext(.4, .2, "Ibias = 20 uA to .1 nA, AmpBias = .5 mA", fontsize = 10)
            # plt.figtext(.4, .25, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            plt.yscale('log')
            plt.title(rowS + '' + colS + '' + str(spec) +" Id vs Vgs")
            plt.xlabel("Vg [V]")
            plt.ylabel("Id [A]")
            plt.legend()
            plt.savefig(picLoc + rowS + colS + ".png")
            fig1 = plt.show(block = False)
            # plt.pause(3)
            plt.close(fig1)
           
        colS = re.sub(r'[0-9]+$',
            lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
            colS)
        currIn = []
        measVg = []
        measVd = []
        commandRX=0
        vdvgData = pd.concat([vdvgData, pltData], axis = 0, ignore_index=True)
    colS = colBegin
    rowS = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the row name
                rowS)   

    vdvgData.to_csv(fileLoc + 'BAK.csv')
commandTX = write_cmd(str(9))                                                   # selects the switch case on the pico
commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
print('pico confirmed: ' + str(commandRX) + ' and turned off.')   
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")    
vdvgData.to_csv(fileLoc + dt_string + '.csv')
print(vdvgData)
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
