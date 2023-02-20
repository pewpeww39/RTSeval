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
smu._write(value='smub.source.autorangev = smub.AUTORANGE_ON')  #set auto range for smua 
smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
# bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
# bkdmm = serial.Serial('com7', 9600)                             #set com port for BK power supply
# def logScale(start, stop, power):
def logScale():
    # powers = power
    # for dec in range(abs(powers)):
    #     start = 10**(power-1)
    #     stop = 10** power
    #     inc = 10**dec
    #     decade = []
    #     stop = 10**power
    #     for i in range(10):
    #         start = start+inc
    #         decade = np.append(decade, range(start, stop))
    #     power = power - 1
    # return decade

    decade1 = range(1,10, 1)
    decade2 = range(10,100, 10)
    decade3 = range(100,1000, 100)
    decade4 = range(1000,10000, 1000)
    decade5 = range(10000,100000, 10000)    
    decade6 = range(100000,1000000, 100000)
    decade7 = range(1000000,11000000, 1000000)
    # decade8 = range(10000000,60000000, 10000000)
    decadeList = np.append(decade1, decade2)
    decadeList = np.append(decadeList, decade3)
    decadeList = np.append(decadeList, decade4)
    decadeList = np.append(decadeList, decade5)
    decadeList = np.append(decadeList, decade6)
    decadeList = np.append(decadeList, decade7) * pow(10, -12)
    # decadeList = np.append(decadeList, decade8) * pow(10, -12)
    # print(len(decadeList))
    return decadeList
    
def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

currIn = []
measVs = []
measVI = []
vGS = []
spec = []
csData = pd.DataFrame(data=[], index=[], columns=[])  
pltData = pd.DataFrame(data=[], index=[], columns=[])         #create dataframe
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W', 'L', 'Type'])
debug = False
row = 0
counter = 0
voltIn = 0
currOut = 0
commandTX = 0
colSelect = 1
rowSelect = 1
power = 9
rowNum = 96
colNum = 32      #int(input('How many colums do you want to test?'))

smu.apply_current(smu.smua, 0.0)
smu.apply_current(smu.smub, 0.0)
colS = "Col000"   
rowS = "Row00"
picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvsCharacterization\\idvscharData"
time.sleep(1)
decadeList = logScale()
# print(decadeList)
for r in range(rowNum):
    for c in range(colNum):
        commandTX = write_cmd(str(4))                                                   # selects the switch case on the pico
        commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
        time.sleep(.5)
        print('pico confirmed: ' + str(commandRX))
        write_cmd(str(rowSelect))                                              # increments the column to test
        rowRX = pico.read_until().strip().decode()                                   # confirms column selected
        print('pico selected row: ' + str(rowRX))
        time.sleep(.5)
        write_cmd(str(colSelect))                                              # increments the column to test
        columnRX = pico.read_until().strip().decode()                                   # confirms column selected
        print('pico selected column: ' + str(columnRX))
        time.sleep(.5)
        commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
        print('pico loaded shift register')
        spec = list(specData.iloc[c+1])
        if commandRX == 1:
            smu.smb.measure.autozero = smub.AUTOZERO_ONCE
            currIn, measVI, measVs = smu.idvgsChar(smu.smua, smu.smub, decadeList, .1, .1)
            vGS = measVs 
            for i in range(len(measVs)):
                vGS[i] = 1.2 - vGS[i]
            pltData["Row"] = rowSelect
            pltData[colS+"Vgs"] = vGS # [1.2 - measVs for i in range(len(measVs))]
            pltData[colS+"Id"] = currIn
            pltData[colS+"Vs"] = measVs
            # csData[colS+'Vs'] = pd.concat([csData[colS+'Vs'], measVs], axis = 0, ignore_index=True)
            # csData[colS+'Id'] =  pd.concat([csData[colS+'Id'], currIn], axis = 0, ignore_index=True)
            # csData[colS+'Vi'] =  pd.concat([csData[colS+'Vi'], measVI], axis = 0, ignore_index=True)
            # csData[colS+'Row'] =  pd.concat([csData[colS+'Row'], rowSelect], axis = 0, ignore_index=True)
            if debug is True:
                print(len(measVs))
                print(vGS)
            plt.plot(vGS, pltData[colS+"Id"], label = "Vs")
            plt.figtext(.8, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            plt.figtext(.8, .2, "Ibias = 1 nA, AmpBias = .5 mA", fontsize = 10)
            plt.figtext(.8, .25, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            plt.yscale('log')
            plt.title(colS + '' + str(spec) +" Id vs Vgs")
            plt.xlabel("Vgs [V]")
            plt.ylabel("Id [A]")
            plt.legend()
            plt.savefig(picLoc + rowS + colS + str(spec) + "idvg.png")
            fig1 = plt.show(block = False)
            # plt.pause(3)
            plt.close(fig1)
            pltData.plot(x=colS+"Id", y=colS+"Vs", xlabel="Current [A]", ylabel="Voltage [V]", sharey=True, title=(colS + '' + 
                            str(spec) + " Current In [Id] vs. Voltage Out [Vs]"), legend=True,
                        subplots=False, logx= True)
            plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            plt.figtext(.2, .2, "Ibias = 1 nA, AmpBias = .5 mA", fontsize = 10)
            plt.figtext(.2, .25, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            plt.savefig(picLoc + rowS + colS + str(spec) + "idvs.png")
            fig2 = plt.show(block = False)
            # plt.pause(3)
            plt.close(fig2)
            colS = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
                colS)
            currIn = []
            measVs = []
            measVI = []
            vGS = []
            row = 0
            power = 9
            commandRX=0
            colSelect = colSelect + 1
    colS = "Col000"   
    colSelect = 1
    rowSelect = rowSelect + 1    
    csData = pd.concat([csData, pltData], axis = 0, ignore_index=False)
    
csData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/idvsCharacterization/idvscharData' + dt_string + '.csv')
print(csData)
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
