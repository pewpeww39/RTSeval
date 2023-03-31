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
# smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
# bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
# bkdmm = serial.Serial('com7', 9600)                             #set com port for BK power supply
# def logScale(start, stop, power):
def logScale():
    decadeList = np.logspace(np.log10(0.0000000001), np.log10(0.00005), 50)
    return decadeList
    
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
    rowEnd = 2 + 1 
    if bank == 1:
        colStart = 1
        colEnd = colStart + 32
        colS = "Col000"   
        rowS = "Row00"
        sweepList = (0.0000000001, (0.00005), 50, 0)
        csIn = 3
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 1\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 1/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 2:
        # colStart = 33
        # colEnd = colStart + 32
        colStart = 53
        colEnd = colStart + 1
        colS = "Col53" # "Col032"   
        rowS = "Row00"
        sweepList = (0.00000000001, 0.005, 50, 0)
        csIn = 3
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 2\\idvgscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 2/idvgscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 3:
        colStart = 65
        colEnd = colStart + 32
        colS = "Col064"   
        rowS = "Row00"
        sweepList = (0.0000000001, (0.00005), 50, 0)
        csIn = 3
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 3\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 3/idvscharData'
        limiti = 0.01
        rangei = pow(10, -2)
    elif bank == 4:
        colStart = 97
        colEnd = colStart + 32
        colS = "Col096"   
        rowS = "Row00"
        sweepList = (0.0000000001, (0.00005), 50, 0)
        csIn = 3
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 4\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 4/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 5:
        colStart = 129
        colEnd = colStart + 32
        colS = "Col128"   
        rowS = "Row00"
        sweepList = (0.0000000001, (0.00005), 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 5\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 5/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 6:
        colStart = 161
        colEnd = colStart + 32
        colS = "Col160"   
        rowS = "Row00"
        sweepList = (0.0000000001, (0.00005), 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 6\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 6/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 7:
        colStart = 193
        colEnd = colStart + 32
        colS = "Col192"   
        rowS = "Row00"
        sweepList = (0.0000000001, (0.00005), 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 7\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 7/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    elif bank == 8:
        colStart = 225
        colEnd = colStart + 32
        colS = "Col224"   
        rowS = "Row00"
        sweepList = (0.0000000001, (0.00005), 50, 0)
        csIn = 6
        picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 8\\idvscharData"
        fileLoc = '~/miniconda3/envs/testequ/RTSeval/Python/Data/idvgsCharacterization/Bank 8/idvscharData'
        limiti = 0.001
        rangei = pow(10, -3)
    return rowStart, rowEnd, colStart, colEnd, colS, rowS, sweepList, csIn, picLoc, fileLoc, limiti, rangei

def powerPico():                                                                    # Turns on the vPwr pins for pi pico
    write_cmd(str(7))                                                               # selects the switch case on the pico
    pico.read_until().strip().decode()                                              # confirms mode selected
    print('pico turned on the power') 
    time.sleep(2)

currIn = []
measVs = []
measVI = []
vGS = []
spec = []
idvgsData = pd.DataFrame(data=[], index=[], columns=[])  
pltData = pd.DataFrame(data=[], index=[], 
                       columns=['Site', 'Type', 'Vs', 'Vgs', 'Id', 'W/L', 'Temp(K)', 'Die X', 'Die Y',
                                 'Vth', 'Gm', 'Swing Factor', 'Row', 'Column', 'Test Time'])                         #create dataframe
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W/L', 'Type'])
debug = False
row = 0
counter = 0
voltIn = 0
currOut = []
commandTX = 0
colSelect = 1
rowSelect = 1
rowNum = 1
colNum = 3      #int(input('How many colums do you want to test?'))
dieX = '6P'
dieY = '3'

rowStart, rowEnd, colStart, colEnd, colS, rowS, sweepList, csIn, picLoc, fileLoc, limiti, rangei = bankNum(2)
colBegin = colS
smu.apply_current(smu.smua, 0.0)
smu.apply_current(smu.smub, 0.0)
powerPico()
# decadeList = logScale()
# print(decadeList)
start_total_time = time.time()
for row in range(rowStart, rowEnd):
    for col in range(colStart, colEnd):
        commandTX = write_cmd(f"{csIn},{row},{col}")                                                   # selects the switch case on the pico
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
        currIn, measVI, measVs = smu.idvgsChar(smu.smua, smu.smub, sweepList, -1, .166)
        pltData["Vs"] = measVs
        pltData['Site'] = 'UTC'
        pltData['Type'] = spec[1]
        vGS = np.full_like(measVs, 1.2) - measVs 
        pltData["Vgs"] = vGS # [1.2 - measVs for i in range(len(measVs))]
        pltData["Id"] = currIn
        pltData["W/L"] = spec[0]
        pltData["Temp(K)"] = 295
        pltData["Die X"] = dieX
        pltData["Die Y"] = dieY
        pltData["Gm"] = np.gradient(currIn, vGS)
        # grouped = pltData.groupby(pltData.Gm)
        # maxGm = max(np.gradient(pltData['Id'], pltData['Vgs'], edge_order=2))
        # vthData = grouped.get_group(max(pltData['Gm']))
        # pltData["Vth"] = (vthData.Vgs*maxGm - np.sqrt(abs(vthData.Id)))/maxGm
        pltData["Row"] = rowSelect
        pltData['Column'] = colSelect
        print(pltData)
        if debug is True:
            print(len(measVs))
            print(vGS)
        if ((col % 2 == 1) and (row <= 2)):
            plt.plot(vGS, pltData["Id"], label = "Vs")
            plt.figtext(.4, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            plt.figtext(.4, .2, "Ibias = 50 uA to .1 nA, AmpBias = .5 mA", fontsize = 10)
            plt.figtext(.4, .25, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            plt.yscale('log')
            plt.title(rowS + '' + colS + '' + str(spec) +" Id vs Vgs")
            plt.xlabel("Vgs [V]")
            plt.ylabel("Id [A]")
            plt.legend()
            plt.savefig(picLoc + rowS + colS + "idvgs.png")
            fig1 = plt.show(block = False)
            # plt.pause(3)
            plt.close(fig1)
            pltData.plot(x="Id", y="Vs", xlabel="Ids [A]", ylabel="Vs [V]", sharey=True, title=(rowS + '' + colS + '' + 
                            str(spec) + " Current In [Id] vs. Voltage Out [Vs]"), legend=True,
                        subplots=False, logx= True)
            plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            plt.figtext(.2, .2, "Ibias = 50 uA to .1 nA, AmpBias = .5 mA", fontsize = 10)
            plt.figtext(.2, .25, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            plt.savefig(picLoc + rowS + colS + "idvs.png")
            fig2 = plt.show(block = False)
            # plt.pause(3)
            plt.close(fig2)
            pltData.plot(x="Vgs", y="Gm", xlabel="Vgs [V]", ylabel="Gm ", sharey=True, title=(rowS + '' + colS + '' + 
                            str(spec) + " Transconductance vs. Vgs [V]"), legend=True,
                        subplots=False, logx= True)
            plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            plt.figtext(.2, .2, "Ibias = 50 uA to .1 nA, AmpBias = .5 mA", fontsize = 10)
            plt.figtext(.2, .2, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            plt.savefig(picLoc + rowS + colS + "gm.png")
            fig3 = plt.show(block = False)
            # plt.pause(3)
            plt.close(fig3)
        colS = re.sub(r'[0-9]+$',
            lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
            colS)
        currIn = []
        measVs = []
        measVI = []
        vGS = []
        commandRX=0
        idvgsData = pd.concat([idvgsData, pltData], axis = 0, ignore_index=True)
    colS = colBegin
    rowS = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the row name
                rowS)   
    # csData = pd.concat([csData, pltData], axis = 0, ignore_index=False)
    idvgsData.to_csv(fileLoc + 'BAK.csv')
commandTX = write_cmd(str(9))                                                   # selects the switch case on the pico
commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
print('pico confirmed: ' + str(commandRX) + ' and reset the shift registers')   

end_total_time = time.time()
test_time = end_total_time - start_total_time
idvgsData.at[0, 'Time'] = test_time
idvgsData.to_csv(fileLoc + dt_string + '.csv')
print(idvgsData)
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
